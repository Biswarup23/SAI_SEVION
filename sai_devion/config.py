import os

APP_NAME = "SAI Devion"
VERSION = "0.1 (BETA)"
API_BASE = "http://127.0.0.1:8000/api/v1"

SIGNUP_URL = f"{API_BASE}/auth/signup"
LOGIN_URL  = f"{API_BASE}/auth/login"
POLISH_URL  = f"{API_BASE}/polish"



# Switch to "http" later when FastAPI backend is ready
# AUTH_MODE = os.getenv("SAI_AUTH_MODE", "mock")  # mock | http

# Backend base (when AUTH_MODE="http")
MAX_WORDS = int(os.getenv("SAI_MAX_WORDS", "500"))

HOTKEY1 = os.getenv("SAI_HOTKEY1", "ctrl+q")
HOTKEY2 = os.getenv("SAI_HOTKEY2", "ctrl+w")

# icons (relative to project root)
ICON_ICO_REL = "icons/app_icon.ico"
ICON_LOGO_REL = "icons/SAI_Gen.png"

# # Signup website (your existing flow)
# # endpoints (future FastAPI)
# SIGNUP_URL = f"{API_BASE}/auth/signup"
#
# LOGIN_URL = f"{API_BASE}/auth/login"
# POLISH_URL = f"{API_BASE}/polish"

# token endpoints (future)
REFRESH_URL = f"{API_BASE}/auth/refresh"
LOGOUT_URL = f"{API_BASE}/auth/logout"
