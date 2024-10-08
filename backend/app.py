import os

import psycopg2
from db import PSQLDriver
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from scraper import Scraper

load_dotenv()

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scraper.html")
def scraper():
    return render_template("scraper.html")


@app.route("/databases", methods=["GET"])
def get_databases():
    p = PSQLDriver()
    p.create_connection()
    db_names = p.get_list_of_tables()
    p.close()
    return jsonify({"databases": db_names})


def get_status_list():
    return ["not applied", "applied", "bookmarked", "manual review", "skipped"]


@app.route("/status", methods=["GET"])
def get_status():
    status_list = get_status_list()
    return jsonify({"status": status_list})


@app.route("/jobs/<status>/<db_name>", methods=["GET"])
def get_jobs(status, db_name):
    # pagination
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        f"SELECT * FROM {db_name} WHERE status = %s ORDER BY job_name ASC LIMIT %s OFFSET %s;",
        (status, per_page, offset),
    )
    rows = cur.fetchall()

    # Get total count of jobs for the specified status
    cur.execute(f"SELECT COUNT(*) FROM {db_name} WHERE status = %s;", (status,))
    total_count = cur.fetchone()[0]

    cur.close()
    conn.close()

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

    # Calculate total pages
    total_pages = (total_count + per_page - 1) // per_page  # Ceiling division

    return jsonify(
        {
            "jobs": jobs,
            "total_pages": total_pages,
            "current_page": page,
        }
    )


@app.route("/jobs/update/", methods=["POST"])
def update_job_status():
    data = request.get_json()

    db_name = data.get("db_name")
    job_name = data.get("job_name")
    new_status = data.get("status")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        f"""
        UPDATE {db_name} 
        SET status = %s 
        WHERE job_name = %s
    """,
        (new_status, job_name),
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Job status updated successfully."}), 200


@app.route("/scrape/", methods=["POST"])
def scrape_data():
    data = request.get_json()
    url = data.get("url")
    table_name = data.get("table_name")

    scraper = Scraper(url, table_name)
    scraper.run()

    return jsonify({"message": "Scraping initiated successfully."}), 200


if __name__ == "__main__":
    app.run(debug=True)
