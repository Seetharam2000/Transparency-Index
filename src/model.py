import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


DATASET_PATH = Path(__file__).parent.parent / "data" / "labeled" / "ec-darkpattern.tsv"
RANDOM_STATE = 42


def load_dataset(dataset_path: Optional[str] = None) -> Tuple[List[str], List[int], List[str]]:
    """Load binary examples and source page IDs from the e-commerce TSV."""
    path = Path(dataset_path) if dataset_path else DATASET_PATH
    with path.open(encoding="utf-8", newline="") as dataset_file:
        rows = list(csv.DictReader(dataset_file, delimiter="\t"))

    required_columns = {"page_id", "text", "label"}
    if not rows or not required_columns.issubset(rows[0]):
        raise ValueError(f"{path} must contain TSV columns: {', '.join(sorted(required_columns))}")

    texts: List[str] = []
    labels: List[int] = []
    page_ids: List[str] = []
    for row_number, row in enumerate(rows, start=2):
        text = row["text"].strip()
        label = row["label"].strip()
        page_id = row["page_id"].strip()
        if not text or not page_id or label not in {"0", "1"}:
            raise ValueError(f"Invalid text, page_id, or binary label on dataset row {row_number}")
        texts.append(text)
        labels.append(int(label))
        page_ids.append(page_id)
    if set(labels) != {0, 1}:
        raise ValueError("The dataset must contain both binary labels 0 and 1.")
    return texts, labels, page_ids


def make_pipeline(classifier) -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    max_features=10000,
                    min_df=2,
                    sublinear_tf=True,
                ),
            ),
            ("classifier", classifier),
        ]
    )


def evaluate_baselines(dataset_path: Optional[str] = None):
    """Evaluate baselines on a page-grouped holdout to reduce site leakage."""
    texts, labels, page_ids = load_dataset(dataset_path)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=RANDOM_STATE)
    train_indices, test_indices = next(splitter.split(texts, labels, groups=page_ids))
    train_groups = {page_ids[index] for index in train_indices}
    test_groups = {page_ids[index] for index in test_indices}
    if train_groups & test_groups:
        raise RuntimeError("Grouped evaluation split leaked a page ID across train and test.")

    train_texts = [texts[index] for index in train_indices]
    train_labels = [labels[index] for index in train_indices]
    test_texts = [texts[index] for index in test_indices]
    test_labels = [labels[index] for index in test_indices]
    if set(train_labels) != {0, 1} or set(test_labels) != {0, 1}:
        raise ValueError("The grouped split must contain both labels in train and test.")

    classifiers = [
        ("Logistic Regression", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)),
        ("Naive Bayes", MultinomialNB()),
        ("SVM", LinearSVC(class_weight="balanced", random_state=RANDOM_STATE)),
    ]
    metrics = []
    for name, classifier in classifiers:
        pipeline = make_pipeline(classifier)
        pipeline.fit(train_texts, train_labels)
        predictions = pipeline.predict(test_texts)
        metrics.append(
            {
                "Model": name,
                "Accuracy": accuracy_score(test_labels, predictions),
                "Precision": precision_score(test_labels, predictions, average="binary", zero_division=0),
                "Recall": recall_score(test_labels, predictions, average="binary", zero_division=0),
                "F1": f1_score(test_labels, predictions, average="binary", zero_division=0),
            }
        )
    return metrics, len(texts), len(test_texts), len(set(page_ids)), len(test_groups)


class DarkPatternClassifier:
    """TF-IDF/logistic-regression classifier for binary e-commerce patterns."""

    LABEL_NAMES = {0: "none", 1: "dark_pattern"}
    CONFIDENCE_THRESHOLD = 0.6

    def __init__(self, dataset_path: Optional[str] = None):
        self.dataset_path = Path(dataset_path) if dataset_path else DATASET_PATH
        self.model: Optional[Pipeline] = None

    def train(self) -> None:
        """Fit on all labeled rows for analysis after evaluation is reported separately."""
        texts, labels, _ = load_dataset(str(self.dataset_path))
        self.model = make_pipeline(
            LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)
        )
        self.model.fit(texts, labels)

    def predict_batch(self, clauses: List[str]) -> List[Dict]:
        """Return binary predictions and dark-pattern probabilities for clauses."""
        if not clauses:
            return []
        if self.model is None:
            self.train()
        if self.model is None:
            raise RuntimeError("Classifier training did not produce a fitted model.")

        probabilities = self.model.predict_proba(clauses)
        predictions = []
        for clause, class_probabilities in zip(clauses, probabilities):
            dark_probability = float(class_probabilities[1])
            label = 1 if dark_probability >= self.CONFIDENCE_THRESHOLD else 0
            predictions.append(
                {
                    "text": clause,
                    "label": self.LABEL_NAMES[label],
                    "confidence": dark_probability if label else 1 - dark_probability,
                    "dark_pattern_probability": dark_probability,
                }
            )
        return predictions
