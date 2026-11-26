from users.user_service import UserService


def test_returns_demo_user():
    user = UserService().get_current_user()
    assert user["id"] == 1
    assert "name" in user