from fastapi import Request, status

from main import app
from fastapi.exceptions import RequestValidationError

from utils.logger import logger_config
from utils.response_handler import response

logger = logger_config(__name__)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error=exc.errors())


@app.exception_handler(ValueError)
def value_error_exception_handler(request: Request, exc: ValueError):
    return response(error=str(exc), status_code=400)


@app.exception_handler(Exception)
def internal_server_error(request: Request, exc: RequestValidationError):
    logger.error(exc)
    return response(error="Internal server error. Please try after some time", status_code=500)
