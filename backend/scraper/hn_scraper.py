import requests
from bs4 import BeautifulSoup as bs

from scraper import db


class Scraper:
    def __init__(self, url):
        # for table name
        self.month = None
        self.year = None
        # {june: 6} mapping
        self.month_to_num = {
            month: i + 1
            for i, month in enumerate(
                [
                    "january",
                    "february",
                    "march",
                    "april",
                    "may",
                    "june",
                    "july",
                    "august",
                    "septmeber",
                    "october",
                    "november",
                    "december",
                ]
            )
        }

        self.PROFILE_LINK = "https://news.ycombinator.com/user?id="
        self.URL = url
        self.count = 0

        self.scraped_data = None
        self.data = {}
        self.misc_data = {}

    def scrape_site(self):
        response = requests.get(self.URL)
        if response.status_code == 200:
            self.scraped_data = response.text

    def extract_table_name(self, soup):
        href = self.URL.split("/")[-1]
        table_name = soup.find("a", href=href).text
        table_name = table_name.split("(")[-1].lower()
        table_name = table_name.split(")")[0].lower()
        month, self.year = table_name.split()
        self.month = self.month_to_num.get(month, 0)

    def extract(self):
        content = self.scraped_data
        soup = bs(content, "html.parser")
        self.extract_table_name(soup)

        posts = soup.find_all("tr", class_="athing comtr")
        self.count = len(posts)

        for i in range(len(posts)):
            post = posts[i]

            try:
                # post
                post_id = posts[i]["id"]
                post_link = f"https://news.ycombinator.com/item?id={post_id}"
            except Exception as e:
                print(f"post: {e}")
                continue

            # content
            try:
                comment = post.select_one("div.commtext")
                links = [a["href"] for a in comment.find_all("a", href=True)]
                header = comment.find(string=True, recursive=False).strip()
                company_name = header.split("|")[0].strip()
                role = "|".join(header.split("|")[1:])
            except Exception as e:
                print(f"content: {e}")
                continue

            try:
                body = comment.find_all("p")
                if len(body) > 0:
                    body = body[0].text
            except Exception as e:
                print(f"body: {e}")

            # author
            try:
                author = post.find("a", class_="hnuser")
                author_name = author.text
                author = {"name": author_name, "link": self.PROFILE_LINK + author_name}
            except Exception as e:
                print(f"author: {e}")
                continue

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

    def push_to_db(self):
        db.create_hnlink(self.month, self.year, self.URL, self.count)

        for company, data in self.data.items():
            db.create_post(self.month, self.year, company, data)

    def run(self):
        try:
            self.scrape_site()
            self.extract()
            self.push_to_db()
            return True
        except Exception as e:
            print(e)
        return False


def main():
    scraper = Scraper("https://news.ycombinator.com/item?id=41425910")
    scraper.run()


if __name__ == "__main__":
    main()
