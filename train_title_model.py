import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

# ✅ Load your data
df = pd.read_csv("data/labeled_resumes.csv")
texts = df["text"]
labels = df["label"]

# ✅ Convert labels to numbers
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(labels)

# ✅ TF-IDF vectorization
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(texts)

# ✅ Train the model
model = XGBClassifier(use_label_encoder=False, eval_metric="mlogloss")
model.fit(X, y)

# ✅ Save model, vectorizer, and label encoder
os.makedirs("ml_model", exist_ok=True)
joblib.dump((vectorizer, model, label_encoder), "ml_model/job_title_predictor.pkl")

print("✅ Model trained and saved to ml_model/job_title_predictor.pkl")
