from typing import Optional

from celery import Celery

from . import scraper

app = Celery("tasks", broker="amqp://guest@queue//")

HOURLY = 60 * 60


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(HOURLY, scrape.s(), name="scrape hourly")


@app.task(name="scrape")
def scrape(url: Optional[str] = None):
    scraper.scrape(url=url)
