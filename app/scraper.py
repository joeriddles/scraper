import logging
import re
from typing import Optional

import bs4
import requests

from app import db
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

    db_service = DbService(Item)
    with db.create_session() as session:
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        for row in soup.find_all("li", class_="result-row"):
            item_id = row["data-pid"]
            url = row.find("a", id=f"postid_{item_id}")["href"]
            logging.info(url)
            text = str(row)
            item = Item(
                item_id=item_id,
                url=url,
                text=text,
            )
            with db_service:
                db_service.add_or_update(Item.item_id == item.item_id, item)


if __name__ == "__main__":
    scrape()
