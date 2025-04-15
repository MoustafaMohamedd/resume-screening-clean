import shap
import joblib
import numpy as np

vectorizer, model, label_encoder = joblib.load("ml_model/job_title_predictor.pkl")
explainer = shap.Explainer(model)

def explain_prediction(text):
    X = vectorizer.transform([text])
    shap_values = explainer(X)
    return shap_values
