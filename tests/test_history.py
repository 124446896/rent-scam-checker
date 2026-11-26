from history.history_repository import HistoryRepository


def make_report(risk="High", reasons=2):
    return {"risk_level": risk, "reasons": [{}] * reasons}


def test_save_and_list(tmp_path):
    repo = HistoryRepository(tmp_path / "test.db")
    repo.save(1, make_report("High", 2))
    checks = repo.list(1)
    assert len(checks) == 1
    assert checks[0]["risk_level"] == "High"
    assert checks[0]["warning_count"] == 2


def test_new_user_has_no_history(tmp_path):
    repo = HistoryRepository(tmp_path / "test.db")
    assert repo.list(99) == []


def test_newest_check_comes_first(tmp_path):
    repo = HistoryRepository(tmp_path / "test.db")
    repo.save(1, make_report("Low", 0))
    repo.save(1, make_report("High", 3))
    assert repo.list(1)[0]["risk_level"] == "High"


def test_users_only_see_their_own_checks(tmp_path):
    repo = HistoryRepository(tmp_path / "test.db")
    repo.save(1, make_report())
    repo.save(2, make_report())
    assert len(repo.list(1)) == 1