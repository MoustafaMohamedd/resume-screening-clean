import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder

# ✅ Load the same labeled data
df = pd.read_csv("data/labeled_resumes.csv")
texts = df["text"]
labels = df["label"]

# ✅ Encode labels to numbers
le = LabelEncoder()
y = le.fit_transform(labels)

# ✅ TF-IDF
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(texts)

# ✅ Train model
model = XGBClassifier(use_label_encoder=False, eval_metric="mlogloss")
model.fit(X, y)

# ✅ Save model + vectorizer + label encoder
os.makedirs("ml_model/models", exist_ok=True)
joblib.dump((vectorizer, model, le), "ml_model/models/resume_classifier.pkl")

print("✅ Resume classifier saved to ml_model/models/resume_classifier.pkl")
