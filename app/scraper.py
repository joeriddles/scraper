import logging
import re
from typing import Optional

import bs4
import requests

from app.db_service import DbService
from app.models.item import Item

URL = "https://spokane.craigslist.org/d/real-estate/search/rea"
USD_PATTERN = re.compile(r"^\$(0|[1-9][0-9]{0,2})(,\d{3})*(\.\d{1,2})?$")


def scrape(url: Optional[str] = None):
    url = url or URL

    response = requests.get(url)
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(str(e))
        return

    soup = bs4.BeautifulSoup(response.text, "html.parser")
    rows = soup.find_all("li", class_="result-row")
    items: list[Item] = []
    for row in rows:
        item_id = row["data-pid"]
        url = row.find("a", id=f"postid_{item_id}")["href"]
        logging.debug(url)
        text = str(row)
        item = Item(
            item_id=item_id,
            url=url,
            text=text,
        )
        items.append(item)

    db_service = DbService(Item)
    with db_service:
        for item in items:
            db_service.add_or_update(Item.item_id == item.item_id, item)


if __name__ == "__main__":
    scrape()
