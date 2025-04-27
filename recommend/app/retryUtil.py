import logging
import sys
import asyncio

logger = logging.getLogger(__name__)
async def retry_with_backoff(
    start_coro_fn,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 30.0
):
    delay = base_delay
    for attempt in range(1, max_retries + 1):
        try:
            return await start_coro_fn()  # 成功则直接返回
        except Exception as e:
            if attempt == max_retries:
                logger.error(
                    f"[{start_coro_fn.__name__}] 启动失败，已重试 {attempt} 次，"
                    "准备退出进程让 Docker 重启", exc_info=e
                )
                sys.exit(1)
            else:
                logger.warning(
                    f"[{start_coro_fn.__name__}] 启动失败 (第 {attempt} 次)：{e!r}，"
                    f"{delay:.1f}s 后重试…"
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, max_delay)