"""Tests for the Apple Reminders MCP server."""

import pytest
from server import sanitize_for_applescript
from dateutil import parser as date_parser


class TestSanitizeForApplescript:
    """Tests for AppleScript input sanitization."""

    def test_sanitize_empty_string(self):
        """Empty string should return empty string."""
        assert sanitize_for_applescript("") == ""

    def test_sanitize_none(self):
        """None should return empty string."""
        assert sanitize_for_applescript(None) == ""

    def test_sanitize_normal_text(self):
        """Normal text without special characters should be unchanged."""
        assert sanitize_for_applescript("Buy groceries") == "Buy groceries"

    def test_sanitize_double_quotes(self):
        """Double quotes should be escaped."""
        assert sanitize_for_applescript('Say "Hello"') == 'Say \\"Hello\\"'

    def test_sanitize_backslashes(self):
        """Backslashes should be escaped."""
        assert sanitize_for_applescript("C:\\Users\\test") == "C:\\\\Users\\\\test"

    def test_sanitize_mixed_special_chars(self):
        """Both quotes and backslashes should be escaped."""
        result = sanitize_for_applescript('Path: "C:\\test"')
        assert result == 'Path: \\"C:\\\\test\\"'

    def test_sanitize_injection_attempt(self):
        """Potential injection attempts should be safely escaped."""
        malicious = '"; do shell script "rm -rf /"; --'
        result = sanitize_for_applescript(malicious)
        # The quotes should be escaped, making the injection harmless
        assert '\\"' in result  # Quotes are escaped
        assert result == '\\"; do shell script \\"rm -rf /\\"; --'


class TestDateParsing:
    """Tests for date parsing."""

    def test_parse_iso_format(self):
        """ISO format dates should parse correctly."""
        result = date_parser.parse("2024-12-25").date()
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 25

    def test_parse_natural_format(self):
        """Natural language dates should parse correctly."""
        result = date_parser.parse("30 January 2026").date()
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 30

    def test_parse_us_format(self):
        """US format dates should parse correctly."""
        result = date_parser.parse("12/25/2024").date()
        assert result.month == 12
        assert result.day == 25

    def test_parse_invalid_date_raises(self):
        """Invalid dates should raise an exception."""
        with pytest.raises(Exception):
            date_parser.parse("not a date at all xyz")
