from unittest.mock import patch

from django.test import TestCase


class FakeProbabilityModel:
    classes_ = (0, 1, 2)

    def predict(self, texts):
        del texts
        return [2]

    def predict_proba(self, texts):
        del texts
        return [[0.1, 0.2, 0.7]]


class FakeDecisionModel:
    classes_ = (0, 1, 2)

    def predict(self, texts):
        del texts
        return [1]

    def decision_function(self, texts):
        del texts
        return [[0.0, 1.0, 2.0]]


class SentimentViewTests(TestCase):
    def test_home_page_offers_both_models(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Normal model")
        self.assertContains(response, "Balanced model")
        self.assertContains(response, "Negative")
        self.assertContains(response, "Neutral")
        self.assertContains(response, "Positive")
        self.assertEqual(response.context["selected_model"], "normal")

    @patch("sentiments.views.load_model", return_value=FakeProbabilityModel())
    def test_balanced_model_returns_prediction_and_three_way_scores(self, load_model):
        response = self.client.post(
            "/",
            {"text": "This is wonderful!", "model": "balanced"},
        )

        self.assertEqual(response.status_code, 200)
        load_model.assert_called_once_with("balanced")
        self.assertEqual(response.context["result"]["sentiment"], "positive")
        self.assertEqual(
            response.context["result"]["scores"],
            {"negative": 10.0, "neutral": 20.0, "positive": 70.0},
        )
        self.assertContains(response, "Positive")

    @patch("sentiments.views.load_model", return_value=FakeDecisionModel())
    def test_normal_model_converts_decision_scores_for_the_meter(self, load_model):
        response = self.client.post(
            "/",
            {"text": "It was okay.", "model": "normal"},
        )

        self.assertEqual(response.status_code, 200)
        load_model.assert_called_once_with("normal")
        self.assertEqual(response.context["result"]["sentiment"], "neutral")
        self.assertEqual(
            response.context["result"]["score_method"],
            "normalized model scores",
        )
        self.assertAlmostEqual(
            sum(response.context["result"]["scores"].values()),
            100.0,
            places=1,
        )

    @patch("sentiments.views.load_model")
    def test_empty_text_and_unknown_model_are_rejected(self, load_model):
        empty_response = self.client.post("/", {"text": "  ", "model": "normal"})
        unknown_model_response = self.client.post(
            "/",
            {"text": "Some text", "model": "unexpected"},
        )

        self.assertEqual(empty_response.status_code, 400)
        self.assertEqual(unknown_model_response.status_code, 400)
        self.assertContains(empty_response, "Enter some text", status_code=400)
        self.assertContains(unknown_model_response, "Choose one", status_code=400)
        load_model.assert_not_called()
