# type: ignore
import requests
import json
import re
from urllib.parse import urlparse

# Your SerpAPI key
API_KEY = "7c33e1742c87325ad914258fdd1758a568ea82b47644793f57a5ae4a9e8e9b68"

SEARCH_QUERIES = {
    "ashby": "site:jobs.ashbyhq.com",
    "lever": "site:jobs.lever.co"
}

OUTPUT_FILES = {
    "ashby": "ashby_companies.json",
    "lever": "lever_companies.json"
}

# works for Lever and Ashby
def extract_company(url) -> None | str:
    """Find company part"""
    parsed = urlparse(url)
    print(parsed)
    parts = parsed.path.strip("/").split("/")
    if not parts:
        return None
    return parts[0]

def fetch_companies(query) -> list:
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": query,
        "api_key": API_KEY,
        "num": 100
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json()
    print(results)

    companies = set()
    for item in results.get("organic_results", []):
        link = item.get("link")
        company = extract_company(link)
        if company:
            companies.add(company)

    return sorted(companies)

def persist_results(domain_type, companies) -> None:
    filename = OUTPUT_FILES[domain_type]
    with open(filename, "w") as f:
        json.dump(companies, f, indent=2)
    print(f"Saved {len(companies)} {domain_type} companies to {filename}")

def main() -> None:
    for domain_type, query in SEARCH_QUERIES.items():
        companies = fetch_companies(query)
        if domain_type == "ashby":
            companies.add("openai")
            companies.add("notion")
        persist_results(domain_type, companies)

if __name__ == "__main__":
    main()