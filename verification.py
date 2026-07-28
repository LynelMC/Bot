import logging

import discord
from discord import app_commands
from discord.ext import commands

import storage

logger = logging.getLogger("verification")

VERIFY_CUSTOM_ID = "verify:button:v1"


class VerifyView(discord.ui.View):
    """
    永続Viewとして main.py の setup_hook で bot.add_view() されるため、
    timeout は必ず None にする。
    """

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="認証する",
        style=discord.ButtonStyle.success,
        emoji="✅",
        custom_id=VERIFY_CUSTOM_ID,
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message("サーバー内でのみ使用できます。", ephemeral=True)
            return

        conf = storage.get_guild_config(guild.id)
        role_id = conf.get("verify_role_id")

        if not role_id:
            await interaction.response.send_message(
                "認証ロールが設定されていません。管理者は `/verify-setup` を実行してください。",
                ephemeral=True,
            )
            return

        role = guild.get_role(role_id)
        if role is None:
            await interaction.response.send_message(
                "設定されている認証ロールが見つかりません。管理者に連絡してください。",
                ephemeral=True,
            )
            return

        member = interaction.user
        if role in member.roles:
            await interaction.response.send_message("すでに認証済みです。", ephemeral=True)
            return

        try:
            await member.add_roles(role, reason="Botによる認証")
        except discord.Forbidden:
            await interaction.response.send_message(
                "ロールを付与する権限がありません。Botのロール順位を確認してください。",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"認証が完了しました！ {role.mention} が付与されました。", ephemeral=True
        )


class Verification(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="verify-setup", description="認証パネルを設置し、付与するロールを設定します")
    @app_commands.describe(
        role="認証時に付与するロール",
        title="埋め込みのタイトル（省略可）",
        description="埋め込みの説明文（省略可）",
    )
    @app_commands.default_permissions(manage_roles=True)
    async def verify_setup(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        title: str = "サーバー認証",
        description: str = "下のボタンを押して認証を完了してください。",
    ):
        if interaction.guild is None:
            await interaction.response.send_message("サーバー内で実行してください。", ephemeral=True)
            return

        # Botより上位のロールは付与できないためチェック
        if interaction.guild.me.top_role <= role:
            await interaction.response.send_message(
                "指定されたロールがBotのロールより上位にあるため付与できません。"
                "Botのロール順位を上げてください。",
                ephemeral=True,
            )
            return

        storage.set_guild_config(interaction.guild.id, verify_role_id=role.id)

        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.green(),
        )
        embed.set_footer(text="Verification System")

        await interaction.response.send_message(embed=embed, view=VerifyView())
        logger.info(f"認証パネルを設置しました guild={interaction.guild.id} role={role.id}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Verification(bot))
