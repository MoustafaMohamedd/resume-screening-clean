import pandas as pd
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

# === Configuration ===
DATA_PATH = "../data/postings.csv"
MODEL_OUTPUT_PATH = "job_title_predictor.pkl"
MAX_FEATURES = 5000
TOP_TITLES = 20
N_ROWS = 500
TEST_SIZE = 0.5
RANDOM_STATE = 42

# === Utility: Text Cleaner ===
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)         # Normalize whitespace
    text = re.sub(r'<.*?>', '', text)        # Remove HTML tags
    return text.strip().lower()

# === Load & Preprocess Data ===
try:
    df = pd.read_csv(DATA_PATH, nrows=N_ROWS)
except FileNotFoundError:
    raise FileNotFoundError(f"❌ Could not find file: {DATA_PATH}")

print("📄 Loaded sample data:")
print(df.head())

df = df[['title', 'description']].dropna()
df['description_clean'] = df['description'].apply(clean_text)

# Limit to top N most frequent job titles
top_titles = df['title'].value_counts().nlargest(TOP_TITLES).index
df = df[df['title'].isin(top_titles)]

# === Split Data ===
X_train, X_test, y_train, y_test = train_test_split(
    df['description_clean'], df['title'],
    test_size=TEST_SIZE, stratify=df['title'], random_state=RANDOM_STATE
)

# === Build Pipeline ===
model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=MAX_FEATURES, stop_words='english')),
    ('clf', LogisticRegression(max_iter=1000))
])

# === Train ===
print("⚙️ Training model...")
model.fit(X_train, y_train)
# ✅ Step 3: Plot and save SHAP
import shap
explainer = shap.Explainer(model)
shap_values = explainer(X)

# Save the SHAP summary plot
import matplotlib.pyplot as plt
shap.summary_plot(shap_values, X, show=False)
plt.savefig("static/shap_summary.png", bbox_inches="tight")
plt.close()

# Save model and vectorizer
joblib.dump((vectorizer, model, label_encoder), "ml_model/job_title_predictor.pkl")
print("✅ Model trained and saved to ml_model/job_title_predictor.pkl")

# === Evaluate ===
y_pred = model.predict(X_test)
print("📊 Evaluation Report:")
print(classification_report(y_test, y_pred))

# === Save ===
joblib.dump(model, MODEL_OUTPUT_PATH)
print(f"✅ Model saved to {MODEL_OUTPUT_PATH}")
