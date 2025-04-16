import time


class TimingMiddleware:
    """
    Измерения времени выполнения запроса.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        start_time = time.time()
        await self.app(scope, receive, send)
        duration = time.time() - start_time
        print(f"Время выполнения запроса: {duration:.4f} секунд")