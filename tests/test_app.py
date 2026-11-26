from app import create_app
from classifier.scam_classifier import ClassifierError


class FailingClassifier:
    """Pretends the AI is down."""

    def classify(self, ad_text):
        raise ClassifierError("AI unavailable")


def make_client(tmp_path, classifier=None):
    app = create_app(classifier=classifier, db_path=tmp_path / "test.db")
    app.config["TESTING"] = True
    return app.test_client()


def test_home_page_loads(tmp_path):
    response = make_client(tmp_path).get("/")
    assert response.status_code == 200
    assert b"Is this rental ad a scam?" in response.data


def test_scam_advert_shows_high_risk(tmp_path):
    ad = "I'm working in Spain. Send the deposit to secure it. Pay in crypto."
    response = make_client(tmp_path).post("/check", data={"ad_text": ad})
    assert response.status_code == 200
    assert b"HIGH RISK" in response.data
    assert b"not a guarantee" in response.data


def test_empty_advert_shows_message(tmp_path):
    response = make_client(tmp_path).post("/check", data={"ad_text": ""})
    assert response.status_code == 400
    assert b"Please paste an advert" in response.data


def test_ai_failure_shows_error_page(tmp_path):
    response = make_client(tmp_path, FailingClassifier()).post("/check", data={"ad_text": "Room in Cork"})
    assert response.status_code == 503
    assert b"couldn't check this advert" in response.data