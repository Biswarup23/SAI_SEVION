from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple, Optional

from sai_devion.session_store import SessionStore, Profile


class AuthService(ABC):
    @abstractmethod
    def signup(self, payload: dict) -> Tuple[bool, str]:
        """Create user account (does NOT log in)."""
        raise NotImplementedError

    @abstractmethod
    def login(self, email: str, password: str, store: SessionStore) -> Tuple[bool, str]:
        """Login with email+password; save profile/tokens to store."""
        raise NotImplementedError

    @abstractmethod
    def try_auto_login(self, store: SessionStore) -> Optional[Profile]:
        """Return Profile if stored session exists and is valid."""
        raise NotImplementedError

    @abstractmethod
    def logout(self, store: SessionStore) -> None:
        """Clear local session and (optionally) revoke tokens."""
        raise NotImplementedError
