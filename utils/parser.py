import os
import pdfplumber
import docx
import re
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# --- SKILL LIST ---
SKILL_KEYWORDS = [
    "python", "java", "c++", "sql", "machine learning", "deep learning", "tensorflow",
    "keras", "pytorch", "nlp", "data science", "excel", "communication", "leadership",
    "project management", "fastapi", "flask", "django", "pandas", "numpy"
]

# --- TEXT EXTRACTION ---

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    else:
        return ""

def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ''
    except Exception as e:
        print(f"PDF read error: {e}")
    return text

def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"DOCX read error: {e}")
    return text

# --- BASIC INFO EXTRACTION ---

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else None

def extract_phone(text):
    match = re.search(r"(\+?\d{1,4}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{4}", text)
    return match.group() if match else None

# --- SKILLS EXTRACTION ---

def extract_skills(text):
    text = text.lower()
    skills_found = []

    for skill in SKILL_KEYWORDS:
        if skill in text and skill not in skills_found:
            skills_found.append(skill)

    return skills_found

# --- FULL RESUME DATA EXTRACTION ---

def extract_resume_data(text):
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text)
    }
def extract_jd_skills(text):
    text = text.lower()
    skills_found = []

    for skill in SKILL_KEYWORDS:
        if skill in text and skill not in skills_found:
            skills_found.append(skill)

    return skills_found

    
