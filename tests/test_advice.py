from advice.advice_service import AdviceService


def test_gives_tip_for_each_category():
    service = AdviceService()
    tips = service.get_advice(["unusual_payment", "pay_before_viewing"])
    assert service.ADVICE["unusual_payment"] in tips
    assert service.ADVICE["pay_before_viewing"] in tips


def test_general_advice_always_included():
    service = AdviceService()
    assert service.GENERAL_ADVICE in service.get_advice([])


def test_unknown_category_is_ignored():
    service = AdviceService()
    assert service.get_advice(["not_a_real_category"]) == [service.GENERAL_ADVICE]


def test_no_duplicate_tips():
    service = AdviceService()
    tips = service.get_advice(["whatsapp_only", "whatsapp_only"])
    assert tips.count(service.ADVICE["whatsapp_only"]) == 1