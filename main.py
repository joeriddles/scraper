import datetime
import logging
import os
import sqlite3

import bs4
import requests

now = datetime.datetime.now().timestamp()
log_path = os.path.join("logs", f"logs-{now}.txt")
if not os.path.exists(log_path):
    file = open(log_path, "w")
    file.close()

file_handler = logging.FileHandler()
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)


URL = "https://spokane.craigslist.org/d/real-estate/search/rea"


def main():
    response = requests.get(URL)
    try:
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(str(e))


if __name__ == "__main__":
    main()
