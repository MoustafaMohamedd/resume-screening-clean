import os

# Security
SECRET_KEY = "supersecretkey123"  # Replace with a secure one in production
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Upload folders
UPLOAD_FOLDER_RESUMES = os.path.join("uploads", "resumes")
UPLOAD_FOLDER_JD = os.path.join("uploads", "job_descriptions")
ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
