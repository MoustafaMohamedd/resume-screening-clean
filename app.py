import os
from flask import Flask, request, render_template, redirect, url_for, flash
from utils.parser import extract_text_from_file, extract_resume_data
from utils.matcher import calculate_match_score
from utils.parser import (
    extract_text_from_file,
    extract_resume_data,
    extract_jd_skills
)



# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'secret_key'  # For flash messages

# File upload settings
app.config['UPLOAD_FOLDER_RESUMES'] = 'resumes'
app.config['UPLOAD_FOLDER_JD'] = 'job_descriptions'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Upload Resume(s)
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        flash('No file part in request')
        return redirect(request.url)

    files = request.files.getlist('resume')
    for file in files:
        if file.filename == '':
            flash('One of the files has no name')
            continue
        if file and allowed_file(file.filename):
            save_path = os.path.join(app.config['UPLOAD_FOLDER_RESUMES'], file.filename)
            file.save(save_path)

    flash('Resume(s) uploaded successfully')
    return redirect(url_for('index'))

# Upload Job Description
@app.route('/upload_jd', methods=['POST'])
def upload_jd():
    jd_file = request.files.get('jd_file')
    if jd_file and allowed_file(jd_file.filename):
        save_path = os.path.join(app.config['UPLOAD_FOLDER_JD'], jd_file.filename)
        jd_file.save(save_path)
        flash('Job description uploaded successfully')
    else:
        flash('Invalid file type for job description')
    return redirect(url_for('index'))

# View Resume Raw Text
@app.route('/view_text/<filetype>/<filename>')
def view_text(filetype, filename):
    if filetype == 'resume':
        folder = app.config['UPLOAD_FOLDER_RESUMES']
    elif filetype == 'jd':
        folder = app.config['UPLOAD_FOLDER_JD']
    else:
        return "❌ Invalid file type"

    file_path = os.path.join(folder, filename)
    if not os.path.exists(file_path):
        return "❌ File not found."

    text = extract_text_from_file(file_path)
    return f"<pre>{text[:5000]}</pre>"  # Limit large files

# Extract Resume Info (Name, Email, Phone, Skills)
@app.route('/extract_info/<filename>')
def extract_info(filename):
    folder = app.config['UPLOAD_FOLDER_RESUMES']
    file_path = os.path.join(folder, filename)

    if not os.path.exists(file_path):
        return "❌ File not found."

    text = extract_text_from_file(file_path)
    info = extract_resume_data(text)
    return f"<pre>{info}</pre>"

# Debug: List uploaded resumes
@app.route('/list_resumes')
def list_resumes():
    files = os.listdir(app.config['UPLOAD_FOLDER_RESUMES'])
    return f"Files in 'resumes/' folder:<br><br>" + "<br>".join(files)
@app.route('/match/<resume_filename>/<jd_filename>')
def match_resume_to_jd(resume_filename, jd_filename):
    resume_path = os.path.join(app.config['UPLOAD_FOLDER_RESUMES'], resume_filename)
    jd_path = os.path.join(app.config['UPLOAD_FOLDER_JD'], jd_filename)

    if not os.path.exists(resume_path) or not os.path.exists(jd_path):
        return "❌ One or both files not found."

    resume_text = extract_text_from_file(resume_path)
    jd_text = extract_text_from_file(jd_path)

    resume_data = extract_resume_data(resume_text)
    jd_skills = extract_jd_skills(jd_text)

    score, matched_skills = calculate_match_score(resume_data["skills"], jd_skills)

    return f"""
    <h2>Matching Result</h2>
    <b>Resume:</b> {resume_filename}<br>
    <b>Job Description:</b> {jd_filename}<br><br>
    <b>Match Score:</b> {score}%<br>
    <b>Matched Skills:</b> {matched_skills}<br>
    <b>Candidate:</b> {resume_data['name']} | {resume_data['email']} | {resume_data['phone']}<br>
    """
@app.route('/match_all/<jd_filename>')
def match_all_resumes(jd_filename):
    jd_path = os.path.join(app.config['UPLOAD_FOLDER_JD'], jd_filename)
    if not os.path.exists(jd_path):
        return "❌ Job description file not found."

    jd_text = extract_text_from_file(jd_path)
    jd_skills = extract_jd_skills(jd_text)

    resume_folder = app.config['UPLOAD_FOLDER_RESUMES']
    resume_files = os.listdir(resume_folder)
    results = []

    for resume_filename in resume_files:
        resume_path = os.path.join(resume_folder, resume_filename)
        resume_text = extract_text_from_file(resume_path)
        resume_data = extract_resume_data(resume_text)
        score, matched_skills = calculate_match_score(resume_data["skills"], jd_skills)

        results.append({
            "filename": resume_filename,
            "name": resume_data.get("name", "Unknown"),
            "email": resume_data.get("email", "N/A"),
            "score": score,
            "matched_skills": matched_skills
        })

    # Sort results by score descending
    ranked = sorted(results, key=lambda x: x["score"], reverse=True)

    html = "<h2>Matching Results (Ranked)</h2><ol>"
    for r in ranked:
        html += f"<li><b>{r['name']}</b> ({r['email']}) – Score: {r['score']}%<br>Matched Skills: {r['matched_skills']}<br><br></li>"
    html += "</ol>"

    return html



# Start the app
if __name__ == '__main__':
    app.run(debug=True)
