# app/middleware/logger.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging
import time

logger = logging.getLogger("uvicorn.access")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        body = await request.body()

        logger.info(
            f"📥 {request.method} {request.url.path} | Body: {body.decode(errors='ignore')}"
        )

        response = await call_next(request)

        duration = round((time.time() - start_time) * 1000)
        logger.info(
            f"📤 {request.method} {request.url.path} completed in {duration}ms with status {response.status_code}"
        )

        return response
