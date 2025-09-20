# type: ignore
import re

# Candidate's known skills (customize)
candidate_skills = {
    "python": ["python"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "sql": ["sql", "postgres", "mysql", "sqlite"],
    "react": ["react", "react.js", "reactjs"],
    "api": ["api", "rest api", "restful", "graphql"],
    "databases": ["database", "db", "nosql", "mongodb", "redis"],
    "cloud": ["aws", "azure", "gcp", "google cloud"]
}

# Mock job fetch function
def fetch_jobs():
    return [
        {
            "title": "Backend Software Engineer",
            "company": "Acme Corp",
            "description": "We are looking for a Python developer with SQL, REST API, and AWS experience."
        },
        {
            "title": "Frontend Developer",
            "company": "Techify",
            "description": "React.js and TypeScript skills required. Bonus points for Node.js and GraphQL."
        },
        {
            "title": "Data Engineer",
            "company": "Datastream",
            "description": "Looking for SQL, Python, and cloud services like GCP or AWS."
        }
    ]

# Extract skills from text
def extract_skills(text, skill_dict):
    found_skills = set()
    text_lower = text.lower()
    for skill, variants in skill_dict.items():
        if any(re.search(rf"\b{re.escape(v)}\b", text_lower) for v in variants):
            found_skills.add(skill)
    return found_skills

# Score job by percentage of JD skills the candidate has
def score_job(jd_text, candidate_skills):
    jd_skills = extract_skills(jd_text, candidate_skills)
    candidate_set = set(candidate_skills.keys())
    overlap = jd_skills & candidate_set
    if not jd_skills:  # avoid division by zero
        return 0.0, jd_skills, overlap
    return len(overlap) / len(jd_skills), jd_skills, overlap

# Main pipeline
def main():
    jobs = fetch_jobs()
    scored_jobs = []
    for job in jobs:
        score, jd_skills, overlap = score_job(job["description"], candidate_skills)
        scored_jobs.append({
            "title": job["title"],
            "company": job["company"],
            "score": round(score * 100, 1),
            "jd_skills": jd_skills,
            "matched_skills": overlap
        })
    
    # Sort by score descending
    scored_jobs.sort(key=lambda x: x["score"], reverse=True)
    
    # Print results
    for job in scored_jobs:
        print(f"{job['title']} at {job['company']} — {job['score']}% match")
        print(f"  JD skills: {', '.join(job['jd_skills'])}")
        print(f"  Matched: {', '.join(job['matched_skills'])}\n")

if __name__ == "__main__":
    main()