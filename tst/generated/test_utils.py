import logging
import pytest
from src.generated.utils import reset_logger


def test_reset_logger_with_default_log_level(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    reset_logger()
    assert logging.getLogger().level == logging.INFO

def test_reset_logger_with_debug_log_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    reset_logger()
    assert logging.getLogger().level == logging.DEBUG

def test_reset_logger_with_invalid_log_level():
    with pytest.raises(AttributeError):
        reset_logger("INVALID_LOG_LEVEL")

def test_reset_logger_with_explicit_log_level():
    reset_logger("WARNING")
    assert logging.getLogger().level == logging.WARNING
