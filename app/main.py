import datetime
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import fastapi
from fastapi.templating import Jinja2Templates

from app import db, worker
from app.db_service import DbService
from app.models.item import Item

BASE_PATH = Path(__file__).resolve().parent


def configure_logging():
    """Configure logging for the application"""
    now = datetime.datetime.now().timestamp()
    log_path = os.path.join("logs", f"logs-{now}.txt")
    if not os.path.exists(log_path):
        file = open(log_path, "w", encoding="utf-8")
        file.close()

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(log_path)
    handlers = (stream_handler, file_handler)
    for handler in handlers:
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)


configure_logging()


app = fastapi.FastAPI()


templates_path = os.path.join(BASE_PATH, "templates")
templates = Jinja2Templates(templates_path)


api_router = fastapi.APIRouter(
    prefix="/api",
    tags=["api"],
)
app.include_router(api_router)


@app.on_event("startup")
def on_startup():
    db.init()


@app.get("/", response_class=fastapi.responses.HTMLResponse)
def index(request: fastapi.Request):
    with DbService(Item) as db_service:
        items = db_service.list()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "items": items,
        },
    )


@api_router.get("/scrape/")
def scrape(url: Optional[str] = None):
    worker.scrape.apply_async((url,))


@api_router.get("/items/")
def items():
    with DbService() as db_service:
        return db_service.list()
