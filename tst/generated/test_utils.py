import logging
import pytest
from src.generated.utils import configure_logging


def test_configure_logging_with_default_log_level(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    configure_logging()
    assert logging.getLogger().level == logging.INFO

def test_configure_logging_with_debug_log_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    configure_logging()
    assert logging.getLogger().level == logging.DEBUG

def test_configure_logging_with_invalid_log_level():
    with pytest.raises(AttributeError):
        configure_logging("INVALID_LOG_LEVEL")

def test_configure_logging_with_explicit_log_level():
    configure_logging("WARNING")
    assert logging.getLogger().level == logging.WARNING
