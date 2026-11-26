import json

RISK_LEVELS = ["Low", "Medium", "High"]


class ClassifierError(Exception):
    """Raised when the AI can't be reached or gives back an answer we can't use."""


class ScamClassifier:
    """The interface for the AI part. Every classifier (fake or real) has this method.

    classify(ad_text) returns a dictionary like:
    {
        "risk_level": "High",
        "warning_signs": [
            {"category": "landlord_abroad", "phrase": "I'm working in Spain", "explanation": "..."}
        ],
        "confidence": 0.8
    }
    """

    def classify(self, ad_text):
        raise NotImplementedError


class MockScamClassifier(ScamClassifier):
    """A fake AI used for testing and for Deliverable 2.

    It gives a realistic answer by looking for a few simple clues, so the rest of
    the app can be built and tested without calling the real AI.
    """

    CLUES = {
        "landlord_abroad": ["abroad", "overseas", "working in"],
        "pay_before_viewing": ["deposit to secure", "send the deposit", "before viewing"],
        "pressure": ["urgent", "lots of interest", "today only"],
    }

    def classify(self, ad_text):
        if not ad_text:
            raise ClassifierError("No advert text was given")

        text = ad_text.lower()
        signs = []
        for category, clues in self.CLUES.items():
            for clue in clues:
                if clue in text:
                    signs.append({
                        "category": category,
                        "phrase": clue,
                        "explanation": f"The advert mentions '{clue}', a common scam warning sign.",
                    })
                    break

        if len(signs) >= 2:
            risk = "High"
        elif len(signs) == 1:
            risk = "Medium"
        else:
            risk = "Low"

        return {"risk_level": risk, "warning_signs": signs, "confidence": 0.5}


class GeminiScamClassifier(ScamClassifier):
    """The real AI classifier using Google Gemini. Planned for Deliverable 3.

    It will send the advert to Gemini with fixed instructions and use
    parse_classifier_output() to check the answer.
    """

    def classify(self, ad_text):
        raise NotImplementedError("The Gemini classifier will be added in Deliverable 3")


def parse_classifier_output(raw_text):
    """Checks the AI's answer is valid JSON in the format we expect.

    Raises ClassifierError if the answer is broken, so the app never shows a
    misleading rating.
    """
    try:
        data = json.loads(raw_text)
    except (json.JSONDecodeError, TypeError):
        raise ClassifierError("The AI's answer was not valid JSON")

    if data.get("risk_level") not in RISK_LEVELS:
        raise ClassifierError("The AI gave an unknown risk level")
    if not isinstance(data.get("warning_signs"), list):
        raise ClassifierError("The AI's answer had no list of warning signs")

    return data


def get_classifier():
    """The ONE place that decides which classifier the app uses.

    To switch from the fake AI to the real one, change MockScamClassifier()
    to GeminiScamClassifier() on the line below.
    """
    return MockScamClassifier()