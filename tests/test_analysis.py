import pytest

from advice.advice_service import AdviceService
from analysis.analysis_service import AnalysisService, redact_personal_details
from classifier.scam_classifier import ClassifierError, MockScamClassifier
from history.history_repository import HistoryRepository
from rules.rule_checker import RuleChecker

USER = {"id": 1, "name": "Demo Student"}


class FakeClassifier:
    """A test classifier that always gives the answer we tell it to."""

    def __init__(self, risk="Low", fail=False):
        self.risk = risk
        self.fail = fail
        self.last_text = None

    def classify(self, ad_text):
        self.last_text = ad_text
        if self.fail:
            raise ClassifierError("AI unavailable")
        return {"risk_level": self.risk, "warning_signs": [], "confidence": 0.5}


def make_service(tmp_path, classifier=None):
    return AnalysisService(
        classifier=classifier or MockScamClassifier(),
        rule_checker=RuleChecker(),
        advice_service=AdviceService(),
        history=HistoryRepository(tmp_path / "test.db"),
    )


# --- Redaction ---

def test_removes_irish_phone_number():
    assert "087" not in redact_personal_details("Call me on 087 123 4567")


def test_removes_international_phone_number():
    assert "353" not in redact_personal_details("Ring +353 87 123 4567 today")


def test_removes_email():
    assert "@" not in redact_personal_details("Email john.rentals@gmail.com")


def test_removes_iban():
    result = redact_personal_details("Pay to IE29 AIBK 9311 5212 3456 78")
    assert "AIBK" not in result


def test_keeps_normal_text():
    text = "Two-bed in Douglas, 1200 a month"
    assert redact_personal_details(text) == text


# --- Full check ---

def test_scam_advert_rated_high(tmp_path):
    ad = "I'm working in Spain. Send the deposit to secure it. Pay in crypto."
    report = make_service(tmp_path).check(ad, USER)
    assert report["risk_level"] == "High"
    assert len(report["reasons"]) > 0


def test_report_always_has_disclaimer_and_advice(tmp_path):
    report = make_service(tmp_path).check("Normal room in Cork, viewing Saturday.", USER)
    assert "not a guarantee" in report["disclaimer"]
    assert len(report["advice"]) >= 1


def test_rules_raise_rating_when_ai_says_low(tmp_path):
    service = make_service(tmp_path, FakeClassifier(risk="Low"))
    report = service.check("Please pay by bitcoin.", USER)
    assert report["risk_level"] == "Medium"


def test_personal_details_removed_before_ai(tmp_path):
    fake = FakeClassifier()
    make_service(tmp_path, fake).check("Text me on 087 123 4567 to view.", USER)
    assert "087" not in fake.last_text


def test_empty_advert_rejected(tmp_path):
    with pytest.raises(ValueError):
        make_service(tmp_path).check("   ", USER)


def test_too_long_advert_rejected(tmp_path):
    with pytest.raises(ValueError):
        make_service(tmp_path).check("a" * 6000, USER)


def test_ai_failure_is_passed_on(tmp_path):
    service = make_service(tmp_path, FakeClassifier(fail=True))
    with pytest.raises(ClassifierError):
        service.check("Room in Cork", USER)


def test_result_saved_to_history(tmp_path):
    service = make_service(tmp_path)
    service.check("Room in Cork, viewing Saturday.", USER)
    assert len(service.history.list(USER["id"])) == 1