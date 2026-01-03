"""
Tests for interval parsing functionality
"""

import pytest

from gh_pr_phase_monitor import parse_interval


class TestParseInterval:
    """Test the parse_interval function"""

    def test_parse_seconds(self):
        """Test parsing seconds"""
        assert parse_interval("30s") == 30
        assert parse_interval("1s") == 1
        assert parse_interval("90s") == 90

    def test_parse_minutes(self):
        """Test parsing minutes"""
        assert parse_interval("1m") == 60
        assert parse_interval("5m") == 300
        assert parse_interval("30m") == 1800

    def test_parse_hours(self):
        """Test parsing hours"""
        assert parse_interval("1h") == 3600
        assert parse_interval("2h") == 7200
        assert parse_interval("24h") == 86400

    def test_parse_days(self):
        """Test parsing days"""
        assert parse_interval("1d") == 86400
        assert parse_interval("2d") == 172800

    def test_case_insensitive(self):
        """Test that parsing is case-insensitive"""
        assert parse_interval("1M") == 60
        assert parse_interval("1H") == 3600
        assert parse_interval("1D") == 86400

    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly"""
        assert parse_interval(" 1m ") == 60
        assert parse_interval("  30s  ") == 30

    def test_invalid_format_no_unit(self):
        """Test that invalid format without unit raises ValueError"""
        with pytest.raises(ValueError, match="Invalid interval format"):
            parse_interval("60")

    def test_invalid_format_no_number(self):
        """Test that invalid format without number raises ValueError"""
        with pytest.raises(ValueError, match="Invalid interval format"):
            parse_interval("m")

    def test_invalid_format_multiple_units(self):
        """Test that invalid format with multiple units raises ValueError"""
        with pytest.raises(ValueError, match="Invalid interval format"):
            parse_interval("1h30m")

    def test_invalid_unit(self):
        """Test that invalid unit raises ValueError"""
        # The regex only accepts units s/m/h/d; this test documents and verifies
        # that unsupported units like "w" are rejected with ValueError.
        with pytest.raises(ValueError, match="Invalid interval format"):
            parse_interval("1w")

    def test_zero_value(self):
        """Test that zero value is allowed"""
        assert parse_interval("0s") == 0
        assert parse_interval("0m") == 0
        assert parse_interval("0h") == 0
        assert parse_interval("0d") == 0

    def test_invalid_type_integer(self):
        """Test that integer input raises ValueError with helpful message"""
        with pytest.raises(ValueError, match="Interval must be a string"):
            parse_interval(60)

    def test_invalid_type_float(self):
        """Test that float input raises ValueError with helpful message"""
        with pytest.raises(ValueError, match="Interval must be a string"):
            parse_interval(1.5)
