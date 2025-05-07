from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging

# Configurar el logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class RequestLoggerMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		# Lógica antes de pasar al siguiente middleware o al endpoint
		logger.info(
			f"Request: {request.method} {request.url} - Headers: {dict(request.headers)}"
		)

		try:
			# Llamamos al siguiente middleware o endpoint
			response = await call_next(request)

			# Lógica después de obtener la respuesta
			logger.info(
				f"Response: {response.status_code} for {request.method} {request.url}"
			)

			# Aquí puedes agregar más detalles si lo necesitas
			return response
		except Exception as e:
			# Manejo de excepciones: si algo falla en el proceso, logueamos el error
			logger.error(
				f"Error processing request {request.method} {request.url} - {str(e)}"
			)
			raise e  # Volver a lanzar la excepción para que FastAPI la maneje correctamente