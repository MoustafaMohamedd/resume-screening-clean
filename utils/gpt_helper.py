import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def suggest_job_titles(skills, api_key=None):
    api_key = api_key or OPENAI_API_KEY
    if not skills:
        return ["❌ No skills provided"]
    if not api_key:
        return ["❌ Missing API key"]

    prompt = (
        "Suggest 3 job titles for a person who has the following skills:\n\n"
        + ", ".join(skills)
        + "\n\nRespond in bullet points."
    )

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful career assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": 100
            }
        )

        data = response.json()
        raw_text = data["choices"][0]["message"]["content"].strip()

        if not raw_text:
            return ["❌ GPT returned empty"]

        # Extract clean titles
        titles = [line.strip("-• ").strip() for line in raw_text.split("\n") if line.strip()]
        return titles if titles else ["❌ Could not parse GPT response"]

    except Exception as e:
        return [f"❌ GPT Error: {str(e)}"]


def suggest_learning_gap(resume_skills, jd_skills, api_key=None):
    api_key = api_key or OPENAI_API_KEY
    if not api_key:
        return ["❌ Missing API key"]
    if not jd_skills:
        return ["❌ No job description skills provided"]

    missing_skills = list(set(jd_skills) - set(resume_skills))
    if not missing_skills:
        return ["✅ No major skill gaps!"]

    prompt = (
        f"A candidate is missing the following job skills: {', '.join(missing_skills)}.\n"
        "Suggest specific learning recommendations, like technologies, topics, or courses to learn them.\n"
        "Respond in bullet points."
    )

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful career advisor."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5,
                "max_tokens": 200
            }
        )

        data = response.json()
        raw_text = data["choices"][0]["message"]["content"].strip()
        suggestions = [line.strip("-• ").strip() for line in raw_text.split("\n") if line.strip()]
        return suggestions if suggestions else ["❌ Could not parse GPT suggestions"]

    except Exception as e:
        return [f"❌ GPT Error: {str(e)}"]
