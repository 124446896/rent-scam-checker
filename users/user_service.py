class UserService:
    """User service (mocked): pretends one demo user is already logged in.

    In the full design this would use real accounts (e.g. Firebase Auth).
    """

    DEMO_USER = {"id": 1, "name": "Demo Student"}

    def get_current_user(self):
        return self.DEMO_USER