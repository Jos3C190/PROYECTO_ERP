"""Settings tests (pure unit — no I/O)."""
from __future__ import annotations

import pytest

from app.core.config import Settings


def test_settings_defaults_to_dev() -> None:
    s = Settings(_env_file=None, ENVIRONMENT="development")
    assert s.ENVIRONMENT == "development"
    assert s.is_production is False
    assert s.ACCESS_TOKEN_EXPIRE_MINUTES == 15


def test_settings_cors_parses_list() -> None:
    s = Settings(_env_file=None, CORS_ORIGINS="http://a.com, http://b.com ,  ")
    assert s.cors_origin_list == ["http://a.com", "http://b.com"]


def test_settings_log_level_uppercased() -> None:
    s = Settings(_env_file=None, LOG_LEVEL="debug")
    assert s.LOG_LEVEL == "DEBUG"


def test_settings_test_env_flag() -> None:
    s = Settings(_env_file=None, ENVIRONMENT="test")
    assert s.is_test is True


def test_environment_variable_taken_from_os(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "x")
    s = Settings()
    assert s.ENVIRONMENT == "production"
    assert s.is_production is True