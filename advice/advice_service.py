class AdviceService:
    """Advice service: gives a safety tip for each type of warning sign."""

    ADVICE = {
        "unusual_payment": "Never pay by crypto, gift cards or money transfer services like Western Union.",
        "pay_before_viewing": "Never pay a deposit before viewing the property in person.",
        "landlord_abroad": "Be very careful if the landlord says they are abroad. Ask to meet them or their agent at the property.",
        "whatsapp_only": "Ask to meet the landlord or agent face to face, not just message them on WhatsApp.",
    }

    # Always shown, even if nothing is found (risk: a scam being rated Low)
    GENERAL_ADVICE = "Always view the property in person before paying anything."

    def get_advice(self, categories):
        """Returns a list of safety tips for the given warning-sign categories."""
        tips = []
        for category in categories:
            tip = self.ADVICE.get(category)
            if tip and tip not in tips:
                tips.append(tip)
        tips.append(self.GENERAL_ADVICE)
        return tips