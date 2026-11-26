import pytest

from classifier.scam_classifier import (
    ClassifierError,
    MockScamClassifier,
    ScamClassifier,
    get_classifier,
    parse_classifier_output,
)


def test_mock_returns_expected_format():
    result = MockScamClassifier().classify("Nice room in Cork, viewing on Saturday.")
    assert result["risk_level"] in ["Low", "Medium", "High"]
    assert isinstance(result["warning_signs"], list)
    assert "confidence" in result


def test_mock_rates_obvious_scam_high():
    ad = "I'm working in Spain at the moment. Send the deposit to secure the room."
    assert MockScamClassifier().classify(ad)["risk_level"] == "High"


def test_mock_rates_normal_advert_low():
    ad = "Two-bed apartment in Douglas. Viewings Saturday with our letting agent."
    assert MockScamClassifier().classify(ad)["risk_level"] == "Low"


def test_mock_rejects_empty_advert():
    with pytest.raises(ClassifierError):
        MockScamClassifier().classify("")


def test_app_uses_a_classifier_through_the_interface():
    assert isinstance(get_classifier(), ScamClassifier)


def test_parse_valid_ai_answer():
    raw = '{"risk_level": "High", "warning_signs": [], "confidence": 0.9}'
    assert parse_classifier_output(raw)["risk_level"] == "High"


def test_parse_rejects_broken_json():
    with pytest.raises(ClassifierError):
        parse_classifier_output("this is not json {")


def test_parse_rejects_unknown_risk_level():
    with pytest.raises(ClassifierError):
        parse_classifier_output('{"risk_level": "Safe", "warning_signs": []}')


def test_parse_rejects_missing_warning_signs():
    with pytest.raises(ClassifierError):
        parse_classifier_output('{"risk_level": "Low"}')