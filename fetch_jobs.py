# type: ignore
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# ==== DATABASE CONFIG ====
DB_NAME = "jobsdb"
DB_USER = "postgres"
DB_PASSWORD = "0H_the0ldman"
DB_HOST = "localhost"
DB_PORT = "5432"

# ==== JOB BOARD API ENDPOINTS ====
GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
LEVER_API = "https://api.lever.co/v0/postings/{company}?mode=json"
ASHBY_API = "https://api.ashbyhq.com/posting-api/job-board/{company}"

# ==== COMPANIES TO QUERY ====
GREENHOUSE_COMPANIES = ["stripe"]
LEVER_COMPANIES = ["instructure", "netflix"]
ASHBY_COMPANIES = ["notion", "snowflake"]

# ==== DATABASE SETUP ====
def init_db():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            source TEXT,
            company TEXT,
            title TEXT,
            location TEXT,
            compensation TEXT,
            description TEXT,
            url TEXT,
            scrape_date DATE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# ==== FETCH FUNCTIONS ====
def fetch_greenhouse():
    jobs = []
    for company in GREENHOUSE_COMPANIES:
        url = GREENHOUSE_API.format(company=company)
        resp = requests.get(url)
        if resp.status_code == 200:
            for job in resp.json().get("jobs", []):
                jobs.append((
                    "Greenhouse",
                    company,
                    job.get("title"),
                    job.get("location", {}).get("name"),
                    None,  # Greenhouse doesn't usually list salary in API
                    requests.get(job["absolute_url"]).text,  # HTML description
                    job["absolute_url"],
                    datetime.today().date()
                ))
    return jobs

def fetch_lever(company):
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    for job in resp.json(): 
        cats = job.get("categories", {}) or {}
        all_locs = cats.get("allLocations")
        all_locs_str = ", ".join(all_locs) if isinstance(all_locs, list) else None

        yield {
            "source": "lever",
            "company": company,
            # "job_id": job.get("id"),
            "title": job.get("text"),
            "commitment": cats.get("commitment"),
            "department": cats.get("department"),
            "location": cats.get("location"),
            "team": cats.get("team"),
            "all_locations": all_locs_str,
            "url": job.get("applyUrl") or job.get("hostedUrl"),
            "job_description": job.get("description") or None,
            "published_at": None  # or job.get("createdAt")
        }

def fetch_ashby():
    jobs = []
    for company in ASHBY_COMPANIES:
        url = ASHBY_API.format(company=company)
        resp = requests.get(url)
        if resp.status_code == 200:
            postings = resp.json().get("jobs", [])
            for job in postings:
                jobs.append((
                    "Ashby",
                    company,
                    job.get("title"),
                    job.get("employmentType"),
                    job.get("department"),
                    job.get("location"),
                    job.get("team"),
                    job.get("compensation"),
                    requests.get(job.get("url")).text,  # HTML description
                    job.get("url"),
                    datetime.today().date()
                ))
    return jobs

# ==== SAVE TO DATABASE ====
def save_jobs(jobs):
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER,
        host=DB_HOST, port=DB_PORT
    )
    cur = conn.cursor()
    insert_query = """
        INSERT INTO jobs
        (source, company, title, location, compensation, description, url, scrape_date)
        VALUES %s
    """
    execute_values(cur, insert_query, jobs)
    conn.commit()
    cur.close()
    conn.close()

# ==== MAIN ====
if __name__ == "__main__":
    init_db()
    all_jobs = []
    all_jobs.extend(fetch_greenhouse())
    all_jobs.extend(fetch_lever())
    all_jobs.extend(fetch_ashby())

    if all_jobs:
        save_jobs(all_jobs)
        print(f"Saved {len(all_jobs)} jobs to Postgres.")
    else:
        print("No jobs found.")