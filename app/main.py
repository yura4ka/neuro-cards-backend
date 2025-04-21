from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core import tasks
import logging

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

app = FastAPI(title="NeuroCards")
app.add_event_handler("startup", tasks.create_start_app_handler(app))
app.add_event_handler("shutdown", tasks.create_stop_app_handler(app))


app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    logger.info("Hello World")
    return {"Hello": "World"}
