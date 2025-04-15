# utils/matcher.py

import os
import requests
import spacy
from dotenv import load_dotenv
from typing import List, Tuple

# Load environment variables
load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Load spaCy model for fallback semantic matching
nlp = spacy.load("en_core_web_md")

# === Synonym Map for Soft Matching ===
SYNONYM_MAP = {
    "communication": ["presentation", "writing", "speaking"],
    "leadership": ["management", "supervision", "mentoring"],
    "python": ["python3", "python 3"],
    "sql": ["database", "mysql", "postgres"]
}


# ✅ 1. Exact Keyword Match
def calculate_match_score(resume_skills: List[str], jd_skills: List[str]) -> Tuple[float, List[str]]:
    if not resume_skills or not jd_skills:
        return 0, []
    matched_skills = list(set(resume_skills).intersection(set(jd_skills)))
    match_percent = (len(matched_skills) / len(jd_skills)) * 100
    return round(match_percent, 2), matched_skills


# ✅ 2. Semantic Similarity Using BERT API (with spaCy fallback)
def get_bert_similarity(text1: str, text2: str) -> float:
    try:
        if not HF_API_TOKEN:
            raise ValueError("No Hugging Face token")

        API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json"
        }

        def get_embedding(text: str) -> List[float]:
            text = text.strip().replace("\n", " ")[:1000]
            response = requests.post(API_URL, headers=headers, json={"inputs": text})
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and isinstance(data[0], list):
                return data[0]
            raise ValueError("Unexpected Hugging Face response format")

        emb1 = get_embedding(text1)
        emb2 = get_embedding(text2)
        dot = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = sum(a**2 for a in emb1) ** 0.5
        norm2 = sum(b**2 for b in emb2) ** 0.5
        return round((dot / (norm1 * norm2)) * 100, 2)

    except Exception as e:
        print(f"[Fallback to spaCy] Reason: {e}")
        doc1, doc2 = nlp(text1), nlp(text2)
        return round(doc1.similarity(doc2) * 100, 2)


# ✅ 3. Feedback Message Generator
def generate_feedback(score: float, matched_skills: List[str], jd_skills: List[str]) -> str:
    missing = list(set(jd_skills) - set(matched_skills))
    if score >= 80:
        msg = "✅ Strong match. Candidate is well-aligned."
    elif score >= 50:
        msg = "⚠️ Moderate match. Some key skills are missing."
    else:
        msg = "❌ Weak match. Candidate lacks several required skills."
    if missing:
        msg += f" Missing: {', '.join(missing[:5])}"
    return msg


# ✅ 4. Synonym Expansion (boost skills with known related terms)
def boost_with_synonyms(skills: List[str]) -> List[str]:
    boosted = set(skills)
    for skill in skills:
        boosted.update(SYNONYM_MAP.get(skill.lower(), []))
    return list(boosted)


# ✅ 5. Semantic Matching with Synonyms (spaCy-based)
def calculate_synonym_boosted_score(resume_skills: List[str], jd_skills: List[str]) -> Tuple[float, List[str]]:
    if not resume_skills or not jd_skills:
        return 0, []

    boosted_resume = boost_with_synonyms(resume_skills)
    matched = set()
    resume_docs = [nlp(skill.lower()) for skill in boosted_resume]
    jd_docs = [nlp(skill.lower()) for skill in jd_skills]

    for res_doc in resume_docs:
        for jd_doc in jd_docs:
            if jd_doc.text in matched:
                continue
            if res_doc.similarity(jd_doc) >= 0.75:
                matched.add(jd_doc.text)
                break

    match_percent = (len(matched) / len(jd_skills)) * 100
    return round(match_percent, 2), list(matched)


# ✅ 6. Bonus: Generate Learning Tip Text
def generate_skill_gap_suggestion(resume_skills: List[str], jd_skills: List[str]) -> str:
    missing = list(set(jd_skills) - set(resume_skills))
    if not missing:
        return "✅ No major skill gaps detected."
    return f"💡 Consider learning: {', '.join(missing[:5])}"
