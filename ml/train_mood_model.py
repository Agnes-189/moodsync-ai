import csv
import os
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, f1_score

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, 'ml', 'dataset', 'mood_dataset.csv')
MODEL_SAVE_PATH = os.path.join(BASE_DIR, 'saved_models', 'mood_classifier.joblib')

def clean_text(text):
    """Lowercase and strip punctuation/extra whitespace."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return re.sub(r'\s+', ' ', text)

def load_dataset():
    texts, labels = [], []
    with open(DATASET_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(clean_text(row['text']))
            labels.append(row['mood'].strip().lower())
    return texts, labels

def train_and_evaluate():
    texts, labels = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    models = {
        "Multinomial Naive Bayes": MultinomialNB(),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42)
    }

    best_model = None
    best_name = ""
    best_f1 = -1.0

    for name, clf in models.items():
        clf.fit(X_train_vec, y_train)
        preds = clf.predict(X_test_vec)
        macro_f1 = f1_score(y_test, preds, average='macro', zero_division=0)

        print(f"\n=== {name} ===")
        print(classification_report(y_test, preds, zero_division=0))
        print("Confusion Matrix:")
        print(confusion_matrix(y_test, preds))

        if macro_f1 >= best_f1:
            best_f1 = macro_f1
            best_model = clf
            best_name = name

    # Retrain winning model on full dataset for production artifact
    full_X_vec = vectorizer.fit_transform(texts)
    best_model.fit(full_X_vec, labels)

    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    artifact = {
        "model_name": best_name,
        "vectorizer": vectorizer,
        "classifier": best_model,
        "classes": list(best_model.classes_)
    }
    joblib.dump(artifact, MODEL_SAVE_PATH)
    print(f"\nSaved winning model ({best_name}) to {MODEL_SAVE_PATH}")

if __name__ == '__main__':
    train_and_evaluate()