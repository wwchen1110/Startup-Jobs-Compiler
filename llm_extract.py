import os
from openai import OpenAI

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---- System instruction ----
SYSTEM_PROMPT = """
You are an information extraction system. Extract a structured tree of skills and their required experience levels from the job description text. 
For each identified skill, if it is a subcategory of another identified skill place it as a sub-field to that field (ex Typescript is a sub-field of Javascript).
The initial super-fields of skills should be: 
  Programming Languages (Python, SQL, JavaScript, TypeScript, Java, C++, etc.) 
  Programming Tools (Git, Docker, APIs, CI/CD, cloud platforms, testing frameworks, etc.) 
  Communication (cross-functional comms, stakeholder alignment, code reviews, conflict resolution, etc.) 
  Ownership (mentorship, initiative, decision-making, driving projects, accountability) 
  Organization (time management, agile methods, documentation, prioritization) 
  Domain Knowledge (finance, healthcare, ML/AI, security, e-commerce, etc.) Do not include typical software developer skills in this super-field. 
If experience level for any skill is mentioned, store the required level as a sub-field of the skill. Rate it from 1 to 10, 1 representing beginner profiency and 10 representing deep expertise. 
If experience level for a skill is not specified, set "level" to null. If sub-skills don't exist, set "skills" to null. 
Return valid JSON ONLY in this format: 
{ 
  "skills": [ 
    {"name": "Programming Languages", "level": 6, "skills": [{"name": "Javascript", "level": null, "skills": [{"name": "Typescript", "level": 3, "skills": null}]}]}, 
    {"name": "Programming Tools", "level": null, "skills": [{"name": "APIs", "level": null, "skills": [{"name": "Notion API", "level": 3, "skills": null}, {"name": "OpenAI API", "level": 1, "skills": null}]}]}, 
    {"name": "Communication", "level": null, "skills": [{"name": "Understanding customer concerns", "level": 7, "skills": null}], "level": "5"}, 
    {"name": "Ownership", "level": null, "skills": [{"name": "Thoroughness", "level": null, "skills": [{"name": "End-to-end ownership of projects", "level": 3, "skills": null}]}]}, 
    {"name": "Organization", "level": null, "skills": null}, 
    {"name": "Domain Knowledge", "level": null, "skills": null} 
  ]
}
"""

def extract_skills_from_jd(jd_text: str) -> dict:
    """Send JD text to LLM and extract skills with experience levels."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": jd_text}
        ],
        temperature=0,  # deterministic extraction
        response_format={ "type": "json_object" }  # ensures strict JSON
    )

    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    jd_text = """
    We are seeking a Senior Data Engineer with 5+ years of experience in Python,
    3+ years working with SQL and ETL pipelines, and familiarity with AWS. 
    Strong communication skills and ability to lead teams is a plus.
    """
    result = extract_skills_from_jd(jd_text)
    print(result)