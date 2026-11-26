from rules.rule_checker import RuleChecker


def test_finds_crypto_payment():
    flags = RuleChecker().check_rules("Lovely room. Please pay the deposit in crypto.")
    assert "unusual_payment" in [f["category"] for f in flags]


def test_finds_several_red_flags():
    ad = "I'm abroad at the moment so WhatsApp only. Send a deposit before viewing."
    categories = [f["category"] for f in RuleChecker().check_rules(ad)]
    assert "landlord_abroad" in categories
    assert "whatsapp_only" in categories
    assert "pay_before_viewing" in categories


def test_ignores_normal_advert():
    ad = "Two-bed apartment in Douglas. Viewings Saturday. Contact our letting agent."
    assert RuleChecker().check_rules(ad) == []


def test_not_case_sensitive():
    flags = RuleChecker().check_rules("PAY BY WESTERN UNION")
    assert flags[0]["category"] == "unusual_payment"


def test_empty_advert_returns_no_flags():
    assert RuleChecker().check_rules("") == []
    assert RuleChecker().check_rules(None) == []