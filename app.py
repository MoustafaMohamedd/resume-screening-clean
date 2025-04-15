# === Imports and Setup ===
import os, csv, io, base64, logging, webbrowser
from datetime import datetime
from functools import wraps
from collections import Counter
from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, send_file
from xhtml2pdf import pisa

# === Internal Modules (Your Own Code) ===
from ml_model.job_title_predictor import predict_job_title, generate_shap_chart
from ml_model.resume_classifier import predict_resume_title
from utils.parser import extract_text_from_file, extract_resume_data, extract_jd_skills, classify_experience
from utils.matcher import (
    calculate_match_score,
    get_bert_similarity,
    generate_feedback,
    calculate_synonym_boosted_score,
    generate_skill_gap_suggestion
)
from utils.database import (
    init_db,
    insert_result,
    get_all_results,
    update_notes_and_rating,
    toggle_star as toggle_star_db
)
from utils.clustering import cluster_resumes
from utils.gpt_helper import suggest_job_titles, suggest_learning_gap
from config import (
    SECRET_KEY,
    ADMIN_USERNAME,
    ADMIN_PASSWORD,
    UPLOAD_FOLDER_RESUMES,
    UPLOAD_FOLDER_JD,
    MAX_CONTENT_LENGTH,
    ALLOWED_EXTENSIONS
)

# === Logging Setup ===
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# === Flask App Setup ===
app = Flask(__name__)
app.config.from_object("config")
app.secret_key = SECRET_KEY

# Create folders for uploads if not already created
os.makedirs(UPLOAD_FOLDER_JD, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_RESUMES, exist_ok=True)

# === Helper Decorators ===
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if session.get("role") != required_role:
                logging.warning(f"[Access Denied] {session.get('role')} tried to access {request.path}")
                
                # ✅ Avoid infinite flash loop
                if request.endpoint != 'admin_dashboard':
                    flash("🚫 Unauthorized access!", "danger")
                
                return redirect(url_for("admin_dashboard"))

            return f(*args, **kwargs)
        return wrapped
    return decorator


# === File Validation ===
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# === Home Page: Show uploaded Job Descriptions ===
@app.route('/')
def index():
    jd_files = os.listdir(app.config['UPLOAD_FOLDER_JD'])
    return render_template('index.html', jd_files=jd_files)

# === Upload Resumes ===
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    files = request.files.getlist('resume')
    for file in files:
        if file and allowed_file(file.filename):
            save_path = os.path.join(app.config['UPLOAD_FOLDER_RESUMES'], file.filename)
            file.save(save_path)
            logging.info(f"[Resume Upload] {session.get('role', 'guest')} uploaded {file.filename}")
    flash("✅ Resume(s) uploaded successfully!")
    return redirect(url_for("index"))

# === Upload Job Descriptions ===
@app.route('/upload_jd', methods=['POST'])
def upload_jd():
    files = request.files.getlist('jd_file')
    for file in files:
        if file and allowed_file(file.filename):
            path = os.path.join(app.config['UPLOAD_FOLDER_JD'], file.filename)
            file.save(path)
            logging.info(f"[JD Upload] {session.get('role', 'guest')} uploaded JD: {file.filename}")
    flash("✅ Job descriptions uploaded successfully!")
    return redirect(url_for("index"))

# === Trigger Resume Matching From UI ===
@app.route('/match_all_selected')
@role_required('admin')
def match_all_selected():
    jd_filename = request.args.get("jd_filename")
    matching_mode = request.args.get("matching_mode")
    skill_weight = request.args.get("skill_weight", "0.5")
    exp_weight = request.args.get("exp_weight", "0.5")
    logging.info(f"[Trigger] Admin started matching for JD: {jd_filename} | Mode: {matching_mode}")
    return redirect(url_for("match_all_resumes",
                            jd_filename=jd_filename,
                            matching_mode=matching_mode,
                            skill_weight=skill_weight,
                            exp_weight=exp_weight))
# === Match All Resumes to Selected JD ===
@app.route('/match_all/<jd_filename>')
@role_required('admin')
def match_all_resumes(jd_filename):
    resumes_folder = app.config['UPLOAD_FOLDER_RESUMES']
    jd_path = os.path.join(app.config['UPLOAD_FOLDER_JD'], jd_filename)
    jd_text = extract_text_from_file(jd_path)
    jd_skills = extract_jd_skills(jd_text)

    results = []
    for filename in os.listdir(resumes_folder):
        if not allowed_file(filename):
            continue
        path = os.path.join(resumes_folder, filename)
        text = extract_text_from_file(path)
        skills, _ = extract_resume_data(text)
        experience_level = classify_experience(text)

        # === ML Prediction: Top-3 titles with confidence
        ml_titles = predict_job_title(text)
        ml_top = ml_titles[0][0]
        confidence = ml_titles[0][1]

        # === GPT Prediction (fallback safe)
        try:
            gpt_title = suggest_job_titles(skills)[0]
        except Exception as e:
            logging.error(f"[GPT FAIL] {e}")
            gpt_title = "❌ GPT Failed"

        disagreement = "⚠️" if gpt_title != ml_top else ""

        # === Matching + Gap + Feedback
        match_score, matched_skills = calculate_match_score(skills, jd_skills)
        feedback = generate_feedback(match_score, matched_skills, jd_skills)
        gaps = generate_skill_gap_suggestion(jd_skills, skills)

        # === Save to DB
        insert_result(
            name="N/A", email="N/A", score=round(match_score, 2),
            skills=", ".join(matched_skills), filename=filename,
            gpt_title=gpt_title, ml_title=ml_top, resume_title=ml_top
        )

        results.append({
            "filename": filename,
            "match_score": round(match_score, 2),
            "matched_skills": matched_skills,
            "predicted_title": ml_top,
            "confidence": confidence,
            "experience_level": experience_level,
            "job_title_suggestions": ml_titles,
            "gpt_title": gpt_title,
            "disagreement": disagreement,
            "feedback": feedback,
            "gaps": gaps
        })

    return render_template("match_result.html", results=results, jd_filename=jd_filename)

# === Admin Dashboard: View Candidates ===
@app.route('/admin')
@role_required('admin')
@login_required
def admin_dashboard():
    # ✅ Get matching mode from the URL or fallback to session or 'exact'
    mode = request.args.get("matching_mode", session.get("matching_mode", "exact"))
    session["matching_mode"] = mode
    skill_weight = float(request.args.get("skill_weight", 0.6))
    exp_weight = float(request.args.get("exp_weight", 0.4))
    starred_only = request.args.get("starred_only")
    session["matching_mode"] = mode

    rows = get_all_results()
    results = []
    for row in rows:
        skills = row[3].split(", ")
        if mode == "semantic":
            semantic_score = get_bert_similarity(" ".join(skills), " ".join(skills))
            skill_score, _ = calculate_match_score(skills, skills)
            score = (skill_weight * skill_score) + ((1 - skill_weight) * semantic_score)
        elif mode == "synonym":
            score, _ = calculate_synonym_boosted_score(skills, skills)
        else:
            score, _ = calculate_match_score(skills, skills)

        text = extract_text_from_file(os.path.join(app.config['UPLOAD_FOLDER_RESUMES'], row[4]))
        ml_titles = predict_job_title(text)

        result = {
            "name": row[0],
            "email": row[1],
            "score": round(score, 2),
            "matched_skills": skills,
            "filename": row[4],
            "notes": row[5],
            "rating": row[6],
            "starred": row[7],
            "experience_level": classify_experience(" ".join(skills)),
            "feedback": generate_feedback(score, skills, []),
            "ml_titles": ml_titles,
            "gpt_title": row[8] if row[8] else "Not found"
        }

        if experience and result["experience_level"] != experience:
            continue
        if result["score"] < min_score or result["score"] > max_score:
            continue
        if starred_only and not result["starred"]:
            continue
        if search and search not in result["name"].lower() and not any(search in s.lower() for s in skills):
            continue

        results.append(result)

        return render_template("admin.html",
                       results=results,
                       matching_mode=mode,      # ✅ Pass to HTML
                       skill_weight=skill_weight,
                       exp_weight=exp_weight)


# === SHAP Explanation per Resume ===
@app.route("/shap/<filename>")
@login_required
def shap_chart(filename):
    from ml_model.job_title_predictor import generate_shap_chart
    generate_shap_chart(filename)
    return render_template("shap_view.html", shap_path=f"shap_{filename}.png", filename=filename)

# === Analytics Dashboard: Visual Charts ===
@app.route('/analytics')
@role_required('admin')
def analytics():
    results = get_all_results()
    scores = [r[2] for r in results if r[2]]
    titles = [r[8] for r in results if r[8]]

    import matplotlib.pyplot as plt

    # Chart 1: Match Score Histogram
    plt.figure(figsize=(5, 3))
    plt.hist(scores, bins=10, color='blue', edgecolor='black')
    plt.title("Match Score Distribution")
    buf1 = io.BytesIO()
    plt.savefig(buf1, format="png")
    buf1.seek(0)
    img1 = base64.b64encode(buf1.read()).decode('utf-8')
    plt.close()

    # Chart 2: Top Titles (GPT)
    top_titles = Counter(titles).most_common(5)
    labels, values = zip(*top_titles) if top_titles else ([], [])
    plt.figure(figsize=(5, 3))
    plt.bar(labels, values, color='green')
    plt.title("Top GPT Job Titles")
    buf2 = io.BytesIO()
    plt.savefig(buf2, format="png")
    buf2.seek(0)
    img2 = base64.b64encode(buf2.read()).decode('utf-8')
    plt.close()

    return render_template("analytics.html", img1=img1, img2=img2)
# === Update Notes & Rating ===
@app.route('/update_note/<filename>', methods=['POST'])
@login_required
def update_note(filename):
    notes = request.form.get("notes", "")
    rating = request.form.get("rating", 0)
    update_notes_and_rating(filename, notes, int(rating))
    flash("✅ Notes and rating updated!", "info")
    return redirect(url_for("admin_dashboard"))

# === Toggle Starred Status for a Resume ===
@app.route('/toggle_star/<filename>')
@login_required
def toggle_star(filename):
    toggle_star_db(filename)
    flash("⭐ Candidate star toggled!", "info")
    return redirect(url_for("admin_dashboard"))

# === Export Results to CSV ===
@app.route('/export_csv')
@login_required
def export_csv():
    rows = get_all_results()
    response = make_response()
    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Email', 'Score', 'Matched Skills', 'Filename',
        'Notes', 'Rating', 'Starred'
    ])
    writer.writerows(rows)
    response.headers['Content-Disposition'] = 'attachment; filename=results.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

# === Export Single Resume as PDF ===
@app.route('/export_pdf/<filename>')
@login_required
def export_pdf(filename):
    resume_path = os.path.join(app.config['UPLOAD_FOLDER_RESUMES'], filename)
    resume_text = extract_text_from_file(resume_path)
    html = render_template("pdf_template.html", filename=filename, text=resume_text)
    result = io.BytesIO()
    pisa.CreatePDF(io.BytesIO(html.encode("utf-8")), dest=result)
    result.seek(0)
    return send_file(result, download_name=f"{filename}_report.pdf", as_attachment=True)

# === Resume Clustering Route ===
@app.route('/cluster')
@login_required
def cluster():
    folder = app.config['UPLOAD_FOLDER_RESUMES']
    resume_texts = []
    filenames = []

    for fname in os.listdir(folder):
        full_path = os.path.join(folder, fname)
        try:
            text = extract_text_from_file(full_path)
            resume_texts.append(text)
            filenames.append(fname)
        except:
            continue

    cluster_labels = cluster_resumes(resume_texts)
    summary = {}
    cluster_results = []

    for i, label in enumerate(cluster_labels):
        tag = f"Cluster {label}"
        summary[tag] = summary.get(tag, 0) + 1
        cluster_results.append({"filename": filenames[i], "label": tag})

    return render_template("clusters.html", clusters=cluster_results,
                           labels=list(summary.keys()), counts=list(summary.values()))

# === Auth: Login Page ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['role'] = 'admin'  # ✅ Optional but recommended
            flash("Login successful!", "info")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("❌ Invalid credentials", "error")
            return redirect(url_for('login'))
    return render_template("login.html")


# === Logout Route ===
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("🔒 Logged out successfully.", "info")
    return redirect(url_for("index"))

# === Test Insert (Dev Only) ===
@app.route("/test_insert")
def test_insert():
    insert_result(
        name="Alice Johnson",
        email="alice@example.com",
        score=88.5,
        skills="Python, SQL, Machine Learning",
        filename="alice_resume.pdf",
        gpt_title="Data Analyst",
        ml_title="ML Engineer",
        resume_title="AI Specialist"
    )
    results = get_all_results()
    output = "<h2>✅ Test Insert Done:</h2><ul>"
    for row in results:
        output += f"<li>{row}</li>"
    output += "</ul>"
    return output

# === Error Handlers ===
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

# === Entrypoint ===
if __name__ == "__main__":
    init_db()
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)
