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
                role TEXT,
                body TEXT,
                status TEXT,
                post_link TEXT,
                links TEXT,
                manual_fix BOOLEAN DEFAULT FALSE
            )
        """)

        for job, data in self.data.items():
            cur.execute(
                f"""
                INSERT INTO {self.table_name} (job_name, author_name, author_link, role, body, status, post_link, links)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (job_name) DO UPDATE SET 
                    author_name = EXCLUDED.author_name,
                    author_link = EXCLUDED.author_link,
                    role = EXCLUDED.role,
                    body = EXCLUDED.body,
                    post_link = EXCLUDED.post_link,
                    links = EXCLUDED.links
                WHERE {self.table_name}.manual_fix = FALSE;
                """,  # ignore status in update
                (
                    job,
                    data["author"]["name"],
                    data["author"]["link"],
                    data["role"],
                    data["body"],
                    data["status"],
                    data["post_link"],
                    data["links"],
                ),
            )

        cur.execute("""
            CREATE TABLE IF NOT EXISTS hn_post (
                table_name TEXT PRIMARY KEY,
                post_link TEXT
            )
        """)

        cur.execute(
            """
                INSERT INTO hn_post (table_name, post_link)
                VALUES (%s, %s)
                ON CONFLICT (table_name) DO UPDATE SET 
                    post_link = EXCLUDED.post_link;
                """,
            (self.table_name, self.URL),
        )

        conn.commit()
        cur.close()
        conn.close()

    def run(self):
        try:
            self.scrape_site()
            self.extract()
            self.push_to_db()
        except Exception as e:
            print("failed", e)

    def load_initial_data(self):
        conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

        cur = conn.cursor()
        cur.execute("""
            DO $$ 
            DECLARE 
                r RECORD;
            BEGIN 
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
                LOOP 
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP; 
            END $$;
        """)

        s = Scraper("https://news.ycombinator.com/item?id=41709301", "oct_24")
        s.run()
        s = Scraper("https://news.ycombinator.com/item?id=41425910", "sept_24")
        s.run()

        conn.commit()
        cur.close()
        conn.close()


def main():
    scraper = Scraper("https://news.ycombinator.com/item?id=41425910", "sept_24")
    scraper.run()


if __name__ == "__main__":
    main()
