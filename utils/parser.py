import os
import re
import pdfplumber
import docx
import spacy
from typing import Optional, Dict, List

# ✅ Load spaCy English language model for name/entity extraction
try:
    nlp = spacy.load("en_core_web_sm")
except:
    raise ImportError("⚠️ Please run: python -m spacy download en_core_web_sm")

# ✅ Predefined skill keywords (extendable)
SKILL_KEYWORDS = [
    "python", "java", "c++", "sql", "machine learning", "deep learning",
    "tensorflow", "keras", "pytorch", "nlp", "data science", "excel",
    "communication", "leadership", "project management", "fastapi",
    "flask", "django", "pandas", "numpy"
]

# ==============================
# 📄 Text Extraction Functions
# ==============================

def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from PDF or DOCX file based on extension.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    return ""  # Unsupported file type

def extract_text_from_pdf(file_path: str) -> str:
    """
    Use pdfplumber to read and extract text from a PDF file.
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[ERROR] PDF read failed: {e}")
    return text

def extract_text_from_docx(file_path: str) -> str:
    """
    Use python-docx to read and extract text from a DOCX file.
    """
    text = ""
    try:
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"[ERROR] DOCX read failed: {e}")
    return text

# ==============================
# 🔎 Field Extraction (NER)
# ==============================

def extract_name(text: str) -> Optional[str]:
    """
    Use spaCy NER to find a person name.
    """
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_email(text: str) -> Optional[str]:
    """
    Extract the first valid email using regex.
    """
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else None

def extract_phone(text: str) -> Optional[str]:
    """
    Extract phone number using regex (flexible to international formats).
    """
    match = re.search(r"(\+?\d{1,4}[\s-]?)?(\(?\d{2,4}\)?[\s-]?)?\d{3,4}[\s-]?\d{4}", text)
    return match.group() if match else None

# ==============================
# 💼 Skill Matching
# ==============================

def extract_skills(text: str) -> List[str]:
    """
    Match predefined skills (case-insensitive).
    """
    text = text.lower()
    return [skill for skill in SKILL_KEYWORDS if skill in text]

def extract_jd_skills(text: str) -> List[str]:
    """
    Same skill extraction logic for job descriptions.
    """
    return extract_skills(text)

# ==============================
# 📋 Resume Summary as Dictionary
# ==============================

def extract_resume_data(text: str) -> Dict[str, Optional[str]]:
    """
    Return structured data dictionary: name, email, phone, skills.
    """
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text)
    }

# ==============================
# 📈 Classify Experience Level
# ==============================

def classify_experience(text: str) -> str:
    """
    Use regex to detect and classify years of experience.
    """
    matches = re.findall(r"(\d+)\+?\s+years?", text.lower())
    if not matches:
        return "Unknown"
    years = max(int(m) for m in matches)
    if years < 2:
        return "Junior"
    elif years < 5:
        return "Mid-Level"
    return "Senior"
