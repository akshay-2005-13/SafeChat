"""
SafeChat - Toxicity Classifier
Uses: unitary/toxic-bert via HuggingFace Transformers
Model: DistilBERT fine-tuned on Jigsaw Toxic Comment dataset
Labels: toxic, severe_toxic, obscene, threat, insult, identity_hate
"""

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch


class ToxicityClassifier:
    """
    Wraps the unitary/toxic-bert model from HuggingFace.
    Classifies text into 6 toxicity categories.
    """

    MODEL_NAME = "unitary/toxic-bert"

    LABELS = [
        "toxic",
        "severe_toxic",
        "obscene",
        "threat",
        "insult",
        "identity_hate"
    ]

    THRESHOLD = 0.5  # Score above this = toxic

    def __init__(self):
        print("[SafeChat] Loading tokenizer and model...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_NAME)
        self.model.eval()
        print("[SafeChat] Model loaded successfully.")

    def classify(self, text: str) -> dict:
        """
        Classifies a text message for toxicity.

        Args:
            text: Input message string

        Returns:
            dict with keys:
                - scores: dict of {label: float} for each category
                - is_toxic: bool — True if any label exceeds threshold
                - top_label: str — highest scoring label
                - top_score: float — highest score value
                - raw_text: original input
        """
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )

        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.sigmoid(logits).squeeze().tolist()

        # Handle single label case
        if isinstance(probs, float):
            probs = [probs]

        # Build scores dict
        scores = {label: round(prob, 4) for label, prob in zip(self.LABELS, probs)}

        # Determine toxicity
        top_label = max(scores, key=scores.get)
        top_score = scores[top_label]
        is_toxic = any(score >= self.THRESHOLD for score in scores.values())

        return {
            "scores": scores,
            "is_toxic": is_toxic,
            "top_label": top_label,
            "top_score": top_score,
            "raw_text": text
        }


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    clf = ToxicityClassifier()

    test_cases = [
        "I love this community, everyone is so helpful!",
        "You are an absolute idiot and I hate you.",
        "I will find you and make you regret this.",
        "This is a normal everyday message about the weather.",
        "Go back to where you came from, you don't belong here.",
    ]

    print("\n── SafeChat Test Results ──\n")
    for msg in test_cases:
        result = clf.classify(msg)
        status = "🔴 TOXIC" if result["is_toxic"] else "🟢 SAFE"
        print(f"Message : {msg[:60]}")
        print(f"Status  : {status}")
        print(f"Top     : {result['top_label']} ({result['top_score']:.2%})")
        print(f"Scores  : {result['scores']}")
        print("─" * 60)
