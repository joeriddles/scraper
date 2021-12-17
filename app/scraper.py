import dataclasses
import logging
import re
import sqlite3
from contextlib import contextmanager
from typing import Optional

import bs4
import requests


@dataclasses.dataclass
class Item:
    item_id: str
    url: str
    text: str


@contextmanager
def connect():
    """Create a cursor connection to the database"""
    connection = sqlite3.connect("items.db")
    cursor = connection.cursor()
    yield cursor
    connection.commit()
    cursor.close()
    connection.close()


def ensure_db_created():
    """Create the database if it does not already exist"""
    with connect() as cursor:
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS items "
            "(item_id TEXT, url TEXT, text TEXT, added DATETIME DEFAULT(STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')))"
        )


def add_item(item: Item, cursor: sqlite3.Cursor):
    cursor.execute(
        "INSERT INTO items (item_id, url, text) VALUES (?, ?, ?)",
        (item.item_id, item.url, item.text),
    )


def list_items(cursor: sqlite3.Cursor) -> list:
    cursor.execute("SELECT item_id, url, added, text FROM items")
    return cursor.fetchall()


URL = "https://spokane.craigslist.org/d/real-estate/search/rea"
USD_PATTERN = re.compile(r"^\$(0|[1-9][0-9]{0,2})(,\d{3})*(\.\d{1,2})?$")


def scrape(url: Optional[str] = None):
    url = url or URL

    ensure_db_created()

    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(str(e))
        return

    with connect() as cursor:
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        for row in soup.find_all("li", class_="result-row"):
            item_id = row["data-pid"]
            url = row.find("a", id=f"postid_{item_id}")["href"]
            logging.info(url)
            text = str(row)
            item = Item(item_id, url, text)
            add_item(item, cursor)


if __name__ == "__main__":
    scrape()
