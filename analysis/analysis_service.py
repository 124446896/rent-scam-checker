import re

RISK_ORDER = ["Low", "Medium", "High"]
MAX_LENGTH = 5000
DISCLAIMER = "This is an AI estimate, not a guarantee. A Low rating does not mean an advert is safe."


def redact_personal_details(text):
    """Removes phone numbers, email addresses and IBANs before anything is sent to the AI."""
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[email removed]", text)
    text = re.sub(r"\bIE\d{2}\s?[A-Z]{4}(\s?\d){14}\b", "[bank details removed]", text, flags=re.IGNORECASE)
    text = re.sub(r"(\+353|\b0)[\d\s-]{7,12}\d", "[phone removed]", text)
    return text


class AnalysisService:
    """Ad analysis service: runs each check from start to finish.

    It only talks to the other parts through their interfaces:
    classifier.classify(), rule_checker.check_rules(),
    advice_service.get_advice() and history.save().
    """

    def __init__(self, classifier, rule_checker, advice_service, history):
        self.classifier = classifier
        self.rule_checker = rule_checker
        self.advice_service = advice_service
        self.history = history

    def check(self, ad_text, user):
        """Checks an advert and returns a report. Raises ValueError for bad input."""
        if not ad_text or not ad_text.strip():
            raise ValueError("Please paste an advert to check.")
        if len(ad_text) > MAX_LENGTH:
            raise ValueError(f"The advert is too long (max {MAX_LENGTH} characters).")

        cleaned = redact_personal_details(ad_text)

        rule_flags = self.rule_checker.check_rules(cleaned)
        ai_result = self.classifier.classify(cleaned)

        risk_level = self._combine_risk(ai_result["risk_level"], rule_flags)

        reasons = list(ai_result["warning_signs"])
        for flag in rule_flags:
            reasons.append({
                "category": flag["category"],
                "phrase": flag["phrase"],
                "explanation": "Matched a known scam red flag.",
            })

        categories = [reason["category"] for reason in reasons]
        report = {
            "risk_level": risk_level,
            "reasons": reasons,
            "advice": self.advice_service.get_advice(categories),
            "disclaimer": DISCLAIMER,
        }

        self.history.save(user["id"], report)
        return report

    def _combine_risk(self, ai_risk, rule_flags):
        """The final rating is the higher of the AI's rating and the rules' rating.

        The rules can push the rating up, but the AI can never bring it down.
        """
        if len(rule_flags) >= 2:
            rule_risk = "High"
        elif len(rule_flags) == 1:
            rule_risk = "Medium"
        else:
            rule_risk = "Low"
        return max(ai_risk, rule_risk, key=RISK_ORDER.index)