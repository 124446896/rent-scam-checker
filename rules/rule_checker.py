class RuleChecker:
    """Rule checker: finds obvious scam red flags by searching for fixed words."""

    RED_FLAGS = {
        "unusual_payment": ["crypto", "bitcoin", "gift card", "western union", "moneygram"],
        "pay_before_viewing": ["deposit before viewing", "deposit before a viewing", "pay before viewing"],
        "landlord_abroad": ["i'm abroad", "i am abroad", "currently abroad", "out of the country"],
        "whatsapp_only": ["whatsapp only", "only on whatsapp", "only via whatsapp"],
    }

    def check_rules(self, ad_text):
        """Returns a list of red flags found, e.g. {"category": "unusual_payment", "phrase": "crypto"}"""
        if not ad_text:
            return []

        text = ad_text.lower()
        flags = []
        for category, phrases in self.RED_FLAGS.items():
            for phrase in phrases:
                if phrase in text:
                    flags.append({"category": category, "phrase": phrase})
                    break
        return flags