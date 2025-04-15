import os
import joblib

MODEL_PATH = os.path.join("ml_model", "models", "resume_classifier.pkl")

try:
    vectorizer, model, label_encoder = joblib.load(MODEL_PATH)
except Exception as e:
    raise RuntimeError(f"❌ Failed to load ML model/vectorizer: {e}")

def predict_resume_title(resume_text):
    if not resume_text.strip():
        return "Unknown", 0.0

    X_input = vectorizer.transform([resume_text])
    prediction = model.predict(X_input)[0]
    confidence = max(model.predict_proba(X_input)[0]) * 100
    predicted_label = label_encoder.inverse_transform([prediction])[0]

    return predicted_label, round(confidence, 2)