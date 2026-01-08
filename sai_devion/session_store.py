import json, os, logging
from dataclasses import dataclass, asdict
import platformdirs

try:
    import keyring
    KEYRING_AVAILABLE = True
except Exception:
    KEYRING_AVAILABLE = False

from sai_devion.config import APP_NAME

SERVICE = "SAI_Devion"  # Credential Manager service



@dataclass
class Profile:
    first_name: str
    middle_name: str | None = None
    last_name: str | None = None
    contact_number: str | None = None
    email: str = ""
    occupation: str | None = None
    country: str | None = None
    subscription: int = 0

class SessionStore:
    """
    Production-safe:
    - profile stored in session.json (non-sensitive)
    - refresh token stored in Windows Credential Manager via keyring
    - access token stored in memory only
    """
    def __init__(self):
        self.dir = platformdirs.user_data_dir(APP_NAME, "SAI_GEN")
        os.makedirs(self.dir, exist_ok=True)
        self.session_file = os.path.join(self.dir, "session.json")

        self._access_token = None
        self._profile: Profile | None = None
        self._load_profile()

    def _load_profile(self):
        if not os.path.exists(self.session_file):
            return
        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            prof = data.get("profile")
            if prof:
                self._profile = Profile(**prof)
        except Exception as e:
            logging.warning(f"Failed to load session: {e}")

    def save_profile(self, profile: Profile):
        self._profile = profile
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump({"profile": asdict(profile)}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.warning(f"Failed to save session: {e}")

    def get_profile(self):
        return self._profile

    def clear_profile(self):
        self._profile = None
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except Exception:
            pass

    def set_access_token(self, token: str | None):
        self._access_token = token

    def get_access_token(self):
        return self._access_token

    def save_refresh_token(self, refresh_token: str):
        if not KEYRING_AVAILABLE:
            raise RuntimeError("Install `keyring` for secure session persistence.")
        keyring.set_password(SERVICE, "refresh_token", refresh_token)

    def load_refresh_token(self):
        if not KEYRING_AVAILABLE:
            return None
        return keyring.get_password(SERVICE, "refresh_token")

    def clear_refresh_token(self):
        if not KEYRING_AVAILABLE:
            return
        try:
            keyring.delete_password(SERVICE, "refresh_token")
        except Exception:
            pass

    def clear_all(self):
        self.set_access_token(None)
        self.clear_refresh_token()
        self.clear_profile()
