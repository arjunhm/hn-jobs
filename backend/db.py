import os
import datetime
import psycopg2
from dotenv import load_dotenv

import logging

logger = logging.getLogger()

load_dotenv()


class PSQLDriver:
    def __init__(self):
        self.dbname = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.conn = None
        self.cur = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
            self.cur = self.conn.cursor()
        except Exception as e:
            logger.error(e)

    # create tables
    def create_hn_post_table(self):
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS hn_post (
                    table_name TEXT PRIMARY KEY,
                    post_link TEXT,
                    count INT,
                    updated_at TIMESTAMP
                );
            """)
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    def create_company_table(self):
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS company (
                    company TEXT PRIMARY KEY,
                    link TEXT,
                    visa TEXT
                )
            """)
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    def create_job_listing_table(self, table_name: str):
        try:
            self.cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
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
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    # insert rows
    def insert_hn_post(self, table_name: str, URL: str, count: int):
        try:
            self.cur.execute(
                """
                    INSERT INTO hn_post (table_name, post_link, count)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (table_name) DO UPDATE SET 
                        post_link = EXCLUDED.post_link,
                        count = EXCLUDED.count;
                    """,
                (table_name, URL, count),
            )
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    def insert_company(self, name: str, link: str, visa: str):
        try:
            self.cur.execute(
                """
                    INSERT INTO company (company, link, visa)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (company) DO UPDATE SET 
                        link = EXCLUDED.link;
                    """,
                (name, link, visa),
            )
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    def insert_job_listing(self, table_name: str, job: str, data: dict):
        try:
            self.cur.execute(
                f"""
                    INSERT INTO {table_name} (
                            job_name, author_name, author_link,
                            role, body, status, post_link, links
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_name) DO UPDATE SET 
                        author_name = EXCLUDED.author_name,
                        author_link = EXCLUDED.author_link,
                        role = EXCLUDED.role,
                        body = EXCLUDED.body,
                        post_link = EXCLUDED.post_link,
                        links = EXCLUDED.links
                    WHERE {table_name}.manual_fix = FALSE;
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

            self.conn.commit()
        except Exception as e:
            logger.error(e)

    # get
    def get_list_of_tables(self):
        try:
            self.cur.execute("""SELECT table_name FROM hn_post;""")
            names = [name[0] for name in self.cur.fetchall()]
            return names
        except Exception as e:
            logger.error(e)
            return []

    def get_hn_post_table(self):
        try:
            self.cur.execute("""SELECT * FROM hn_post;""")
            return self.cur.fetchall()
        except Exception as e:
            logger.error(e)
            return []

    def get_job_postings(self, table, status, per_page, offset):
        try:
            self.cur.execute(
                f"SELECT * FROM {table} WHERE status = %s ORDER BY job_name ASC LIMIT %s OFFSET %s;",
                (status, per_page, offset),
            )
            return self.cur.fetchall()
        except Exception as e:
            logger.error(e)
            return []

    def get_row_count(self, table_name, status):
        try:
            self.cur.execute(
                f"SELECT COUNT(*) FROM {table_name} WHERE status = %s;", (status,)
            )
            return self.cur.fetchone()[0]
        except Exception as e:
            logger.error(e)
            return 0

    # update
    def update_status(self, table_name, status, job_name):
        try:
            self.cur.execute(
                f"""
                UPDATE {table_name} 
                SET status = %s 
                WHERE job_name = %s
            """,
                (status, job_name),
            )
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    def update_hn_post(self, table_name: str, count: int):
        try:
            self.cur.execute(
                """
                UPDATE hn_post
                SET count = %s
                SET updated_at = %s
                WHERE table_name = %s
                """,
                (count, datetime.datetime.now(), table_name),
            )
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    # drop
    def drop_all_tables(self):
        try:
            self.cur.execute("""
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
            self.conn.commit()
        except Exception as e:
            logger.error(e)

    def close(self):
        try:
            self.conn.commit()
            self.cur.close()
            self.conn.close()
        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    p = PSQLDriver()
    p.connect()
    p.create_hn_post_table()
    p.close()
