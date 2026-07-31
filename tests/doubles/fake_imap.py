"""IMAP test double implementing the subset used by CrmIMAP."""

from __future__ import annotations

from typing import Any


class FakeIMAP4SSL:
    """Minimal imaplib.IMAP4_SSL stand-in for credential wiring tests."""

    login_calls: list[tuple[str, str]] = []

    def __init__(self, host: str, port: int = 993) -> None:
        self.host = host
        self.port = port
        self.state = 'LOGOUT'

    @classmethod
    def reset(cls) -> None:
        cls.login_calls = []

    def login(self, user: str, password: str) -> tuple[str, Any]:
        type(self).login_calls.append((user, password))
        self.state = 'AUTH'
        return 'OK', [b'Logged in']

    def noop(self) -> tuple[str, Any]:
        return 'OK', [b'NOOP completed']

    def logout(self) -> tuple[str, Any]:
        self.state = 'LOGOUT'
        return 'OK', [b'Logout completed']

    def select(self, mailbox: str = 'INBOX') -> tuple[str, Any]:
        return 'OK', [b'1']

    def uid(self, command: str, *args: str) -> tuple[str, Any]:
        return 'OK', [b'']
