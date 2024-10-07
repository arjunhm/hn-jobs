import json
import os

import psycopg2
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
from db import PSQLDriver

load_dotenv()


class Scraper:
    def __init__(self, url, table_name):
        self.psql_driver = PSQLDriver()
        self.table_name = table_name

        self.PROFILE_LINK = "https://news.ycombinator.com/user?id="
        self.URL = url
        self.scraped_data_file = f"{self.table_name}_data.txt"
        self.data_file = f"{self.table_name}_data.json"
        self.misc_file = f"{self.table_name}_misc_data.json"
        self.data = {}
        self.misc_data = {}

    def scrape_site(self):
        response = requests.get(self.URL)
        if response.status_code == 200:
            with open(self.scraped_data_file, "w", encoding="utf-8") as fp:
                fp.write(response.text)

    def get_scraped_data(self):
        with open(self.scraped_data_file, encoding="utf-8") as fp:
            content = fp.read()
        return content

    def extract(self):
        content = self.get_scraped_data()
        soup = bs(content, "html.parser")
        posts = soup.find_all("tr", class_="athing comtr")

        for i in range(len(posts)):
            post = posts[i]

            # post
            post_id = posts[i]["id"]
            post_link = f"https://news.ycombinator.com/item?id={post_id}"

            # content
            comment = post.select_one("div.commtext")
            links = " ".join([a["href"] for a in comment.find_all("a", href=True)])
            header = comment.find(text=True, recursive=False).strip()
            company_name = header.split("|")[0].strip()
            role = "|".join(header.split("|")[1:])
            try:
                body = comment.find_all("p")[0].text
            except:
                continue

            # author
            author = post.find("a", class_="hnuser")
            author_name = author.text
            author = {"name": author_name, "link": self.PROFILE_LINK + author_name}

            if len(role) > 100:
                role = ""
                body = role

            if ("|" not in role) and ("|" not in role):
                self.misc_data[i] = {
                    "author": author,
                    "body": body,
                    "post_link": post_link,
                }
                continue

            self.data[company_name] = {
                "author": author,
                "role": role,
                "body": body,
                "status": "not applied",
                "post_link": post_link,
                "links": links,
            }
        print(len(self.data))

    def dump(self):
        with open(self.data_file, "w") as fp:
            json.dump(self.data, fp, indent=2)

        with open(self.misc_file, "w") as fp:
            json.dump(self.misc_data, fp, indent=2)

    def push_to_db(self):
        self.psql_driver.create_job_listing_table(self.table_name)

        for job, data in self.data.items():
            self.psql_driver.insert_job_listing(self.table_name, job, data)

        self.psql_driver.create_hn_post_table()
        self.psql_driver.insert_hn_post(self.table_name, self.URL)

        self.psql_driver.close()

    def run(self):
        try:
            self.scrape_site()
            self.extract()
            self.push_to_db()
        except Exception as e:
            print("failed", e)

    def load_initial_data(self):
        self.psql_driver.drop_all_tables()
        s = Scraper("https://news.ycombinator.com/item?id=41709301", "oct_24")
        s.run()
        s = Scraper("https://news.ycombinator.com/item?id=41425910", "sept_24")
        s.run()


def main():
    scraper = Scraper("https://news.ycombinator.com/item?id=41425910", "sept_24")
    scraper.run()


if __name__ == "__main__":
    main()
