from scraper import Scraper
from db import PSQLDriver

psql_driver = PSQLDriver()
psql_driver.connect()

psql_driver.create_hn_post_table()
psql_driver.create_company_table()

URLS = [
    "https://news.ycombinator.com/item?id=38842977",
    "https://news.ycombinator.com/item?id=39217310",
    "https://news.ycombinator.com/item?id=39562986",
    "https://news.ycombinator.com/item?id=39894820",
    "https://news.ycombinator.com/item?id=40224213",
    "https://news.ycombinator.com/item?id=40563283",
    "https://news.ycombinator.com/item?id=40846428",
    "https://news.ycombinator.com/item?id=41129813",
    "https://news.ycombinator.com/item?id=41425910",
    "https://news.ycombinator.com/item?id=41709301",
]

n = len(URLS)
for i, url in enumerate(URLS):
    Scraper(url).run()
    print(f"{i+1}/{n} done")

print("Setup done")
