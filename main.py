import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from config.config import get_config

# provide path to .env file , path is relative to project root
settings = get_config()

openapi_url = None
if os.environ["ENV"] == "DEV":
    openapi_url = "/openapi.json"

app = FastAPI(openapi_url=openapi_url)


if __name__ == "__main__":
    # include routes
    from api.routes.apiRoutes import routers
    from config.celery.celery import make_celery
    from utils.logger import logger_config
    from config.database.mongo import MongoManager

    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(routers)

    # prometheus metrics: https://prometheus.io/
    # app.add_middleware(PrometheusMiddleware)
    # app.add_route("/metrics", handle_metrics)

    celery = make_celery()
    logger = logger_config(__name__)

    @app.on_event("startup")
    async def startup():
        logger.info("db connection startup")
        await MongoManager().connect_to_database(settings.DB_URI)

    @app.on_event("shutdown")
    async def shutdown():
        logger.info("db connection stutdown")
        await MongoManager.close_database_connection()


# if __name__ == "__main__":
#     uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)
