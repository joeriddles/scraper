import datetime
import logging
import os
import sys
from typing import Optional

import fastapi

from . import scraper, worker


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


@app.get("/", response_class=fastapi.responses.HTMLResponse)
def index():
    return "<html>Hello world 👋</html>"


@app.get("/scrape/")
def scrape(url: Optional[str] = None):
    worker.scrape.apply_async((url,))


@app.get("/items/")
def items():
    with scraper.connect() as cursor:
        return scraper.list_items(cursor)
