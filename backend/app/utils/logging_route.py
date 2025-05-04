from fastapi.routing import APIRoute
import logging

logger = logging.getLogger(__name__)

class LoggingRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request, *args, **kwargs):
            body = await request.body()
            logger.info(f"📨 [{request.method}] {request.url} – Payload: {body.decode(errors='ignore')}")
            response = await original_route_handler(request, *args, **kwargs)
            logger.info(f"✅ Response status: {response.status_code}")
            return response

        return custom_route_handler
