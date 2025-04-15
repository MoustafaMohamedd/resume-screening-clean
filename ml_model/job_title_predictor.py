import joblib
import numpy as np

MODEL_PATH = "ml_model/job_title_predictor.pkl"

try:
    vectorizer, model, label_encoder = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"❌ Failed to load job title model: {e}")

def predict_job_title(text):
    X = vectorizer.transform([text])
    probs = model.predict_proba(X)[0]
    top_indices = np.argsort(probs)[::-1][:3]
    top_titles = [(label_encoder.inverse_transform([i])[0], round(probs[i] * 100, 2)) for i in top_indices]
    return top_titles
def get_top_title_only(text):
    return predict_job_title(text)[0][0]


def generate_shap_chart(filename):
    import shap
    import matplotlib.pyplot as plt
    from utils.parser import extract_text_from_file
    import os

    text_path = os.path.join("uploads", "resumes", filename)
    resume_text = extract_text_from_file(text_path)
    X = vectorizer.transform([resume_text])

    explainer = shap.Explainer(model)
    shap_values = explainer(X)

    plt.figure(figsize=(10, 5))
    shap.plots.bar(shap_values[0], show=False)
    plt.savefig(f"static/shap_{filename}.png")
    plt.close()
