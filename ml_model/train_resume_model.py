import os
import re
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report
from xgboost import XGBClassifier

# === Configuration ===
DATA_PATH = "../data/labeled_resumes.csv"
MODEL_PATH = "resume_classifier.pkl"
ENCODER_PATH = "resume_label_encoder.pkl"
MAX_FEATURES = 5000
TOP_CLASSES = 10
TEST_SIZE = 0.2
RANDOM_STATE = 42

# === Utility: Clean Text ===
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'<.*?>', '', text)
    return text.strip().lower()

# === Load Dataset ===
try:
    df = pd.read_csv(DATA_PATH)
    print(f"📄 Loaded dataset with {len(df)} entries.")
except FileNotFoundError:
    raise FileNotFoundError(f"❌ File not found: {DATA_PATH}")

# === Clean & Filter ===
df['cleaned_text'] = df['text'].apply(clean_text)

# Focus on top N classes only
top_labels = df['label'].value_counts().nlargest(TOP_CLASSES).index
df = df[df['label'].isin(top_labels)]

# === Encode Labels ===
label_encoder = LabelEncoder()
df['encoded_label'] = label_encoder.fit_transform(df['label'])

# === Split Dataset ===
X_train, X_test, y_train, y_test = train_test_split(
    df['cleaned_text'],
    df['encoded_label'],
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=df['encoded_label']
)

# === Define Pipeline ===
model = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=MAX_FEATURES, stop_words='english')),
    ('clf', XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        eval_metric='mlogloss',
        use_label_encoder=False,
        verbosity=0
    ))
])

# === Train Model ===
print("⚙️ Training XGBoost resume classifier...")
model.fit(X_train, y_train)

# === Evaluate ===
y_pred = model.predict(X_test)
print("\n📊 Resume Classifier Evaluation:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_, zero_division=0))

# === Save Artifacts ===
joblib.dump(model, MODEL_PATH)
joblib.dump(label_encoder, ENCODER_PATH)
print(f"✅ Saved: {MODEL_PATH} and {ENCODER_PATH}")
