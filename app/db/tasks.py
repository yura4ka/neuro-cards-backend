from fastapi import FastAPI
from databases import Database
from app.core.config import settings
import logging

logger = logging.getLogger("uvicorn.error")


async def connect_to_db(app: FastAPI) -> None:
    database = Database(settings.db_url, min_size=2, max_size=10)

    try:
        logger.info("--- Connection to DB ---")
        await database.connect()
        logger.info("--- Connection to DB successful ---")
        app.state._db = database
    except Exception as e:
        logger.error("--- DB CONNECTION ERROR ---")
        logger.error(e)
        logger.error("--- DB CONNECTION ERROR ---")


async def close_db_connection(app: FastAPI) -> None:
    try:
        await app.state._db.disconnect()
    except Exception as e:
        logger.warning("--- DB DISCONNECT ERROR ---")
        logger.warning(e)
        logger.warning("--- DB DISCONNECT ERROR ---")
