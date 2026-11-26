from flask import Flask, render_template, request

from advice.advice_service import AdviceService
from analysis.analysis_service import AnalysisService
from classifier.scam_classifier import ClassifierError, get_classifier
from history.history_repository import HistoryRepository
from rules.rule_checker import RuleChecker
from users.user_service import UserService


def create_app(classifier=None, db_path="history.db"):
    """Builds the app. Acts as the simplified API gateway: it routes each
    request to the right part of the system."""
    app = Flask(__name__)

    analysis = AnalysisService(
        classifier=classifier or get_classifier(),
        rule_checker=RuleChecker(),
        advice_service=AdviceService(),
        history=HistoryRepository(db_path),
    )
    users = UserService()

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/check", methods=["POST"])
    def check():
        ad_text = request.form.get("ad_text", "")
        user = users.get_current_user()
        try:
            report = analysis.check(ad_text, user)
        except ValueError as error:
            # Bad input (empty or too long): show the message on the home page
            return render_template("index.html", error=str(error), ad_text=ad_text), 400
        except ClassifierError:
            # The AI failed: show the error page with general safety advice
            return render_template("error.html"), 503
        return render_template("result.html", report=report)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)