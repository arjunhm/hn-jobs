import json
import os

import psycopg2
import requests
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv

load_dotenv()


class Scraper:
    def __init__(self, url, table_name):
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
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

        timestamp = soup.find_all("span", class_="age")
        authors = soup.find_all("a", class_="hnuser")
        comments = soup.find_all("div", class_="commtext")

        for i in range(len(comments)):
            post_link = timestamp[i].find("a")["href"]

            author_name = authors[i].text
            author = {"name": author_name, "link": self.PROFILE_LINK + author_name}

            comment_text = comments[i].text
            if ("|" not in comment_text) and ("|" not in comment_text):
                self.misc_data[i] = {
                    "author": author,
                    "body": comment_text,
                    "post_link": "https://news.ycombinator.com/" + post_link,
                }
                continue

            parts = comment_text.split("|")
            company_name = parts[0].strip()
            metadata = "|".join(parts[1:-1]).strip()
            body = parts[-1].strip()

            if len(metadata) > 100:
                metadata = ""
                body = metadata

            self.data[company_name] = {
                "author": author,
                "metadata": metadata,
                "body": body,
                "status": "not applied",
                "post_link": "https://news.ycombinator.com/" + post_link,
            }

    def dump(self):
        with open(self.data_file, "w") as fp:
            json.dump(self.data, fp, indent=2)

        with open(self.misc_file, "w") as fp:
            json.dump(self.misc_data, fp, indent=2)

    def test(self):
        with open(self.data_file) as fp:
            data = json.load(fp)
        with open(self.misc_file) as fp:
            misc_data = json.load(fp)

        print("data=", len(data))
        print("misc=", len(misc_data))

    def push_to_db(self):
        conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

        cur = conn.cursor()
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                job_name TEXT PRIMARY KEY,
                author_name TEXT,
                author_link TEXT,
                metadata TEXT,
                body TEXT,
                status TEXT,
                post_link TEXT
            )
        """)

        for job, data in self.data.items():
            cur.execute(
                f"""
                INSERT INTO {self.table_name} (job_name, author_name, author_link, metadata, body, status, post_link)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_name) DO NOTHING
                """,
                (
                    job,
                    data["author"]["name"],
                    data["author"]["link"],
                    data["metadata"],
                    data["body"],
                    data["status"],
                    data["post_link"],
                ),
            )

        conn.commit()
        cur.close()
        conn.close()

    def run(self):
        self.scrape_site()
        self.extract()
        # self.dump()
        # self.test()
        self.push_to_db()


def main():
    scraper = Scraper()
    scraper.run()


if __name__ == "__main__":
    main()
