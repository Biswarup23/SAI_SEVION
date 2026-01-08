import requests
from typing import Optional, Tuple

from sai_devion.config import LOGIN_URL, SIGNUP_URL
from sai_devion.session_store import SessionStore, Profile


class HttpAuthService:
    """
    Desktop-side HTTP auth client for FastAPI backend.
    Backend contract:
      - POST /auth/signup -> 200/201 {message}
      - POST /auth/login  -> 200 {access_token, refresh_token, profile:{...}}
    """

    def signup(self, payload: dict) -> Tuple[bool, str]:
        try:
            r = requests.post(SIGNUP_URL, json=payload, timeout=15)
            if r.status_code in (200, 201):
                return True, "Signup successful. Verify your email, then login."

            try:
                data = r.json()
                msg = data.get("detail") or data.get("message") or str(data)
            except Exception:
                msg = r.text or "Signup failed"
            return False, msg

        except Exception as e:
            return False, str(e)

    def login(self, email: str, password: str, store: SessionStore):
        try:
            payload = {"email": email.strip().lower(), "password": password}
            r = requests.post(LOGIN_URL, json=payload, timeout=15)

            # Always helpful for debugging production issues
            # (remove prints later if you want)
            print("LOGIN_URL:", LOGIN_URL)
            print("LOGIN_STATUS:", r.status_code)
            print("LOGIN_BODY:", r.text)

            if r.status_code == 200:
                data = r.json()

                # ✅ Accept different server shapes:
                # Shape A: {access_token, refresh_token, profile:{...}}
                access_token = data.get("access_token") or data.get("access") or ""
                refresh_token = data.get("refresh_token") or data.get("refresh") or ""
                prof = data.get("profile") or data.get("user") or {}

                # Shape B: {access_token, refresh_token, first_name, email, ...} (profile flattened)
                if not prof:
                    prof = data

                # Validate minimum fields
                if not refresh_token:
                    return False, f"Server did not return refresh_token. Body: {data}"

                if not prof.get("email") and not prof.get("first_name"):
                    return False, f"Server did not return profile fields. Body: {data}"

                profile = Profile(
                    first_name=prof.get("first_name") or "",
                    middle_name=prof.get("middle_name"),
                    last_name=prof.get("last_name"),
                    contact_number=prof.get("contact_number"),
                    email=prof.get("email") or email.strip().lower(),
                    occupation=prof.get("occupation"),
                    country=prof.get("country"),
                    subscription=int(prof.get("subscription", 0)),
                )

                if access_token:
                    store.set_access_token(access_token)

                store.save_refresh_token(refresh_token)
                store.save_profile(profile)
                return True, "Login successful."

            # Non-200 -> show backend error message
            try:
                data = r.json()
                msg = data.get("detail") or data.get("message") or str(data)
            except Exception:
                msg = r.text or "Login failed"
            return False, msg

        except Exception as e:
            return False, str(e)

    def try_auto_login(self, store: SessionStore):
        """
        Auto-login if:
          - profile exists in session.json
          - refresh token exists in keyring
        """
        prof = store.get_profile()
        refresh = store.load_refresh_token()
        if prof and refresh:
            return prof
        return None

    def logout(self, store: SessionStore) -> None:
        # For now: clear local session. Later: call backend revoke endpoint.
        store.clear_all()
