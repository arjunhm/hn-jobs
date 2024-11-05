import logging
import os
from logging.config import dictConfig

import psycopg2
from db import PSQLDriver
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from scraper import Scraper

load_dotenv()

log_dir = "log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(module)s - %(levelname)s - %(funcName)s - %(message)s",
            },
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": "log/app.log",
                "level": "INFO",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "ERROR",
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["file", "console"],
        },
    }
)

app = Flask(__name__)
logger = logging.getLogger(__name__)


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


# Templates


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scraper.html")
def scraper():
    return render_template("scraper.html")


@app.route("/company.html")
def company():
    return render_template("company.html")


@app.route("/tables", methods=["GET"])
def get_tables():
    tables = psql_driver.get_list_of_tables()
    return jsonify({"data": tables})


# Helper


def get_status_list():
    return ["all", "not applied", "applied", "bookmarked", "manual review", "skipped"]


# Views


@app.route("/status", methods=["GET"])
def get_status():
    status_list = get_status_list()
    return jsonify({"status": status_list})


@app.route("/jobs/<status>/<table_name>", methods=["GET"])
def get_jobs(status, table_name):
    # pagination
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    offset = (page - 1) * per_page
    search = request.args.get("search")
    tags = request.args.get("tags")

    rows, total_count = psql_driver.get_job_postings(
        table_name, status, search, tags, per_page, offset
    )

    jobs = []
    for row in rows:
        jobs.append(
            {
                "job_name": row[0],
                "author_name": row[1],
                "author_link": row[2],
                "role": row[3],
                "body": row[4],
                "status": row[5],
                "post_link": row[6],
                "links": row[7],
            }
        )

    total_pages = (total_count + per_page - 1) // per_page
    return jsonify(
        {
            "data": jobs,
            "total_pages": total_pages,
            "current_page": page,
        }
    )


@app.route("/jobs/update/", methods=["POST"])
def update_job_status():
    data = request.get_json()

    table_name = data.get("table_name")
    job_name = data.get("job_name")
    new_status = data.get("status")

    psql_driver.update_status(table_name, new_status, job_name)

    return jsonify({"message": "Job status updated successfully."}), 200


@app.route("/scrape/", methods=["POST"])
def scrape_data():
    data = request.get_json()
    url = data.get("url")
    table_name = data.get("table_name")

    scraper = Scraper(url)
    scraper.run()

    return jsonify({"message": "Scraping initiated successfully."}), 200


@app.route("/companies/", methods=["GET"])
def get_companies():
    # pagination
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 30))
    offset = (page - 1) * per_page

    rows, total_count = psql_driver.get_companies(per_page, offset)
    companies = []
    for row in rows:
        companies.append({"company": row[0], "link": row[1], "visa": row[2]})

    total_pages = (total_count + per_page - 1) // per_page
    return jsonify(
        {
            "data": companies,
            "total_pages": total_pages,
            "current_page": page,
        }
    )


@app.route("/company/jobs/", methods=["GET"])
def get_company_jobs():
    name = request.args.get("company")
    if name is None:
        return jsonify(None)

    rows = psql_driver.get_company_jobs(name)
    jobs = []
    for row in rows:
        if len(row) > 0:
            row = row[0]
            jobs.append(
                {
                    "job_name": row[0],
                    "author_name": row[1],
                    "author_link": row[2],
                    "role": row[3],
                    "body": row[4],
                    "status": row[5],
                    "post_link": row[6],
                    "links": row[7],
                    "table": row[9],
                }
            )

    return jsonify({"data": jobs})


def initialize_tables():
    psql_driver.create_hn_post_table()
    psql_driver.create_company_table()


@app.route("/update/", methods=["POST"])
def update_data():
    data = psql_driver.get_all_from_hn_post()
    for row in data:
        link = row[1]
        print(f"{link=}")
        Scraper(link).run()
    return jsonify({"message": "Updated successfully."}), 200


if __name__ == "__main__":
    psql_driver = PSQLDriver()
    psql_driver.connect()

    psql_driver.create_hn_post_table()
    psql_driver.create_company_table()

    app.run(debug=True)
