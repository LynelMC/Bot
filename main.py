import asyncio
import logging
import os

import discord
from discord.ext import commands

from keep_alive import start_web_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bot")

TOKEN = os.environ.get("DISCORD_TOKEN")

INTENTS = discord.Intents.default()
INTENTS.members = True          # 認証機能でロール付与するために必要
INTENTS.message_content = True  # プレフィックスコマンドを使う場合に必要


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=INTENTS, help_command=None)

    async def setup_hook(self):
        # Cog（機能拡張）の読み込み
        for ext in ("cogs.verification", "cogs.embed_tool"):
            await self.load_extension(ext)

        # 認証ボタンはBot再起動後も反応する必要があるので、
        # 永続Viewとして登録しておく
        from cogs.verification import VerifyView
        self.add_view(VerifyView())

        # スラッシュコマンドを同期
        synced = await self.tree.sync()
        logger.info(f"スラッシュコマンドを {len(synced)} 件同期しました")

    async def on_ready(self):
        logger.info(f"ログインしました: {self.user} (ID: {self.user.id})")
        await self.change_presence(
    activity=discord.Activity(
        type=discord.ActivityType.playing,
        name="NaruBot"
    )
        )


async def main():
    if not TOKEN:
        raise RuntimeError(
            "環境変数 DISCORD_TOKEN が設定されていません。"
            "Renderの Environment 設定でトークンを登録してください。"
        )

    # RenderはPORTでHTTPを受け付けるプロセスを要求するため、
    # Discord Botと並行して簡易HTTPサーバーを起動する
    await start_web_server()

    bot = MyBot()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
