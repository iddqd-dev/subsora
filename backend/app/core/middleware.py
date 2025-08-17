from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logging.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {process_time:.2f}s"
        )
        return response