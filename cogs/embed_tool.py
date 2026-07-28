import logging
import re

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger("embed_tool")

HEX_COLOR_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")


def parse_color(value: str | None) -> discord.Color:
    if not value:
        return discord.Color.blurple()
    if not HEX_COLOR_RE.match(value):
        return discord.Color.blurple()
    return discord.Color(int(value.lstrip("#"), 16))


class EmbedModal(discord.ui.Modal, title="Embedを作成"):
    embed_title = discord.ui.TextInput(
        label="タイトル", placeholder="お知らせ", required=False, max_length=256
    )
    embed_description = discord.ui.TextInput(
        label="本文",
        style=discord.TextStyle.paragraph,
        placeholder="内容を入力してください",
        required=False,
        max_length=4000,
    )
    embed_color = discord.ui.TextInput(
        label="色 (HEXコード。例: #5865F2)", required=False, max_length=7
    )
    embed_image = discord.ui.TextInput(
        label="画像URL（省略可）", required=False
    )
    embed_footer = discord.ui.TextInput(
        label="フッター（省略可）", required=False, max_length=256
    )

    def __init__(self, target_channel: discord.abc.Messageable):
        super().__init__()
        self.target_channel = target_channel

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=self.embed_title.value or None,
            description=self.embed_description.value or None,
            color=parse_color(self.embed_color.value),
        )

        if self.embed_image.value:
            embed.set_image(url=self.embed_image.value)

        if self.embed_footer.value:
            embed.set_footer(text=self.embed_footer.value)

        embed.set_author(
            name=str(interaction.user), icon_url=interaction.user.display_avatar.url
        )

        try:
            await self.target_channel.send(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(
                "そのチャンネルに送信する権限がありません。", ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"{self.target_channel.mention} に送信しました。", ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        logger.exception("Embed作成中にエラーが発生しました", exc_info=error)
        if interaction.response.is_done():
            await interaction.followup.send("エラーが発生しました。", ephemeral=True)
        else:
            await interaction.response.send_message("エラーが発生しました。", ephemeral=True)


class EmbedTool(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="embed", description="フォームからEmbedメッセージを作成して送信します")
    @app_commands.describe(channel="送信先チャンネル（省略時は実行したチャンネル）")
    @app_commands.default_permissions(manage_messages=True)
    async def embed_command(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | None = None,
    ):
        target = channel or interaction.channel
        await interaction.response.send_modal(EmbedModal(target_channel=target))


async def setup(bot: commands.Bot):
    await bot.add_cog(EmbedTool(bot))
