from sai_devion.auth_service import AuthService
from sai_devion.session_store import SessionStore, Profile


class MockAuthService(AuthService):
    def __init__(self):
        self._users = {}  # email -> payload

    def signup(self, payload: dict):
        email = (payload.get("email") or "").strip().lower()
        if not email:
            return False, "Email is required."
        if email in self._users:
            return False, "Email already exists."
        self._users[email] = payload
        return True, "Signup successful. Verify your email, then login."

    def login(self, email: str, password: str, store: SessionStore):
        e = email.strip().lower()
        if e not in self._users:
            return False, "Account not found. Please sign up."

        # In mock we won't really validate password (optional: validate payload["password"])
        u = self._users[e]

        profile = Profile(
            first_name=u.get("first_name") or "User",
            middle_name=u.get("middle_name"),
            last_name=u.get("last_name"),
            contact_number=u.get("contact_number"),
            email=e,
            occupation=u.get("occupation"),
            country=u.get("country"),
            subscription=0
        )

        try:
            store.save_refresh_token("mock_refresh")
        except Exception:
            pass

        store.save_profile(profile)
        return True, "Logged in (mock)."

    def try_auto_login(self, store: SessionStore):
        rt = store.load_refresh_token()
        prof = store.get_profile()
        if rt and prof:
            return prof
        return None

    def logout(self, store: SessionStore):
        store.clear_all()
