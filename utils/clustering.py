from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Optional: Label mapping for clearer labels in UI
DEFAULT_LABELS = ["Tech-heavy", "Managerial", "Business-oriented", "Creative"]

def cluster_resumes(resume_texts, num_clusters=3, label_map=None):
    """
    Cluster resumes into groups using TF-IDF + KMeans.
    
    Args:
        resume_texts (list): List of resume text strings.
        num_clusters (int): Number of clusters to generate.
        label_map (list): Optional list of human-readable cluster labels.

    Returns:
        list of dict: [{'label': 'Tech-heavy', 'filename': 'resume1.pdf'}, ...]
    """
    if not resume_texts:
        return []

    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X = vectorizer.fit_transform(resume_texts)

    model = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(X)

    # Use fallback labels if none provided
    label_map = label_map or DEFAULT_LABELS
    readable_labels = [label_map[i % len(label_map)] for i in labels]

    return readable_labels
