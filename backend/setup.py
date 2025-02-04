from scraper import Scraper
from db import PSQLDriver

psql_driver = PSQLDriver()
psql_driver.connect()

psql_driver.create_hn_post_table()
psql_driver.create_company_table()

URLS = [
    "https://news.ycombinator.com/item?id=42919502",
    "https://news.ycombinator.com/item?id=42575537"
]

n = len(URLS)
for i, url in enumerate(URLS):
    Scraper(url).run()
    print(f"{i+1}/{n} done")

print("Setup done")
