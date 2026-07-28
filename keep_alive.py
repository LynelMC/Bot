import logging
import os

from aiohttp import web

logger = logging.getLogger("keep_alive")


async def handle_root(request: web.Request) -> web.Response:
    return web.Response(text="Discord Bot is running.")


async def handle_health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def start_web_server() -> None:
    """
    Renderは指定した PORT でHTTPリクエストを受け付けるプロセスを要求する
    (Web Service としてデプロイする場合)。
    Discord Bot自体はHTTPサーバーを必要としないため、
    ヘルスチェック用の最小限のサーバーをここで別途起動する。
    """
    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_get("/health", handle_health)

    port = int(os.environ.get("PORT", 8080))

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()

    logger.info(f"HTTPサーバーを起動しました (port={port})")
