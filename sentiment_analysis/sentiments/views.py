import math
from functools import lru_cache
from pathlib import Path

import joblib
from django.conf import settings
from django.shortcuts import render


MODEL_OPTIONS = {
    "normal": {
        "name": "Normal model",
        "path": "sentimentscope_model.pkl",
    },
    "balanced": {
        "name": "Balanced model",
        "path": "sentimentscope_balanced_model.pkl",
    },
}

SENTIMENTS = ("negative", "neutral", "positive")
CLASS_TO_SENTIMENT = {
    "0": "negative",
    "1": "neutral",
    "2": "positive",
    **{sentiment: sentiment for sentiment in SENTIMENTS},
}


@lru_cache(maxsize=2)
def load_model(model_name):
    model_path = Path(settings.BASE_DIR) / "models" / MODEL_OPTIONS[model_name]["path"]
    return joblib.load(model_path)


def _sentiment_for_class(class_label):
    sentiment = CLASS_TO_SENTIMENT.get(str(class_label).strip().casefold())
    if sentiment is None:
        raise ValueError(f"Unsupported sentiment class: {class_label}")
    return sentiment


def _sentiment_scores(model, text):
    classes = [_sentiment_for_class(class_label) for class_label in model.classes_]
    if set(classes) != set(SENTIMENTS):
        raise ValueError("The selected model must contain negative, neutral, and positive classes.")

    if hasattr(model, "predict_proba"):
        raw_scores = model.predict_proba([text])[0]
        score_method = "model probabilities"
    elif hasattr(model, "decision_function"):
        decision_scores = model.decision_function([text])[0]
        decision_scores = [float(score) for score in decision_scores]
        if len(decision_scores) != len(classes):
            raise ValueError("The selected model returned an unexpected number of sentiment scores.")
        highest_score = max(decision_scores)
        raw_scores = [
            math.exp(score - highest_score)
            for score in decision_scores
        ]
        score_method = "normalized model scores"
    else:
        raise ValueError("The selected model does not provide sentiment scores.")

    scores = [float(score) for score in raw_scores]
    if len(scores) != len(classes) or any(not math.isfinite(score) or score < 0 for score in scores):
        raise ValueError("The selected model returned invalid sentiment scores.")

    score_total = sum(scores)
    if score_total <= 0:
        raise ValueError("The selected model returned empty sentiment scores.")

    percentages = {
        sentiment: round(score / score_total * 100, 1)
        for sentiment, score in zip(classes, scores)
    }
    return percentages, score_method


def home(request):
    context = {
        "models": MODEL_OPTIONS,
        "selected_model": "normal",
        "text": "",
        "result": None,
        "error": None,
    }

    if request.method == "POST":
        text = request.POST.get("text", "").strip()
        selected_model = request.POST.get("model", "normal")
        context["text"] = text
        context["selected_model"] = selected_model if selected_model in MODEL_OPTIONS else "normal"

        if not text:
            context["error"] = "Enter some text before analyzing its sentiment."
        elif selected_model not in MODEL_OPTIONS:
            context["error"] = "Choose one of the available sentiment models."
        else:
            model = load_model(selected_model)
            prediction = _sentiment_for_class(model.predict([text])[0])
            scores, score_method = _sentiment_scores(model, text)
            context["result"] = {
                "sentiment": prediction,
                "scores": scores,
                "score_rows": [
                    {"label": sentiment, "value": scores[sentiment]}
                    for sentiment in SENTIMENTS
                ],
                "model_name": MODEL_OPTIONS[selected_model]["name"],
                "score_method": score_method,
            }

        if context["error"]:
            return render(request, "home.html", context, status=400)

    return render(request, "home.html", context)
