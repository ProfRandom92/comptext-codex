"""Tests for security and validation module."""

import pytest
from comptext_codex.security import (
    InputValidator,
    RateLimiter,
    SecurityAuditor,
    validate_command,
    audit_command,
    rate_limit
)
import time


class TestInputValidator:
    """Test cases for InputValidator."""

    def test_valid_command(self):
        """Test validation of valid command."""
        validator = InputValidator()
        result = validator.validate("@A:compress text")

        assert result.valid is True
        assert len(result.errors) == 0

    def test_command_too_long(self):
        """Test validation fails for too long command."""
        validator = InputValidator()
        long_command = "x" * 20000
        result = validator.validate(long_command)

        assert result.valid is False
        assert any("maximum length" in err for err in result.errors)

    def test_dangerous_pattern_eval(self):
        """Test detection of dangerous eval pattern."""
        validator = InputValidator()
        result = validator.validate("@A:compress eval('malicious')")

        assert result.valid is False
        assert any("dangerous pattern" in err for err in result.errors)

    def test_dangerous_pattern_import(self):
        """Test detection of dangerous import pattern."""
        validator = InputValidator()
        result = validator.validate("@A:compress import os")

        assert result.valid is False
        assert any("dangerous pattern" in err for err in result.errors)

    def test_unbalanced_brackets(self):
        """Test detection of unbalanced brackets."""
        validator = InputValidator()
        result = validator.validate("@CMD[param")

        assert result.valid is False
        assert any("Unbalanced brackets" in err for err in result.errors)

    def test_excessive_bracket_depth(self):
        """Test detection of excessive bracket nesting."""
        validator = InputValidator()
        nested = "@CMD[" * 15 + "x" + "]" * 15
        result = validator.validate(nested)

        assert result.valid is False
        assert any("nesting depth" in err for err in result.errors)

    def test_too_many_chained_commands(self):
        """Test detection of too many chained commands."""
        validator = InputValidator()
        chained = " + ".join(["@A:cmd"] * 25)
        result = validator.validate(chained)

        assert result.valid is False
        assert any("Too many chained" in err for err in result.errors)

    def test_null_byte_detection(self):
        """Test detection of null bytes."""
        validator = InputValidator()
        result = validator.validate("@A:compress\x00malicious")

        assert result.valid is False
        assert any("null bytes" in err for err in result.errors)

    def test_sanitization(self):
        """Test input sanitization."""
        validator = InputValidator()
        result = validator.validate("@A:compress  extra   spaces  ")

        assert result.valid is True
        assert result.sanitized_input == "@A:compress extra spaces"

    def test_bracket_depth_calculation(self):
        """Test bracket depth calculation."""
        validator = InputValidator()

        # Simple case
        assert validator._check_bracket_depth("[]") == 1

        # Nested
        assert validator._check_bracket_depth("[[]]") == 2

        # Complex
        assert validator._check_bracket_depth("[a[b[c]]]") == 3

    def test_balanced_brackets_check(self):
        """Test balanced brackets checking."""
        validator = InputValidator()

        assert validator._check_balanced_brackets("[]") is True
        assert validator._check_balanced_brackets("[()]") is True
        assert validator._check_balanced_brackets("[") is False
        assert validator._check_balanced_brackets("[)") is False


class TestRateLimiter:
    """Test cases for RateLimiter."""

    def test_within_limit(self):
        """Test requests within limit."""
        limiter = RateLimiter(max_requests=5, window_seconds=1)

        for _ in range(5):
            assert limiter.check_rate_limit("user1") is True

    def test_exceeds_limit(self):
        """Test request exceeding limit."""
        limiter = RateLimiter(max_requests=3, window_seconds=1)

        for _ in range(3):
            limiter.check_rate_limit("user1")

        assert limiter.check_rate_limit("user1") is False

    def test_window_expiry(self):
        """Test rate limit resets after window."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)

        limiter.check_rate_limit("user1")
        limiter.check_rate_limit("user1")

        # Should be rate limited
        assert limiter.check_rate_limit("user1") is False

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        assert limiter.check_rate_limit("user1") is True

    def test_different_users(self):
        """Test rate limits are per-user."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)

        limiter.check_rate_limit("user1")
        limiter.check_rate_limit("user1")

        # user1 is rate limited
        assert limiter.check_rate_limit("user1") is False

        # user2 is not rate limited
        assert limiter.check_rate_limit("user2") is True

    def test_get_remaining_requests(self):
        """Test getting remaining requests."""
        limiter = RateLimiter(max_requests=5, window_seconds=1)

        assert limiter.get_remaining_requests("user1") == 5

        limiter.check_rate_limit("user1")
        assert limiter.get_remaining_requests("user1") == 4

        limiter.check_rate_limit("user1")
        limiter.check_rate_limit("user1")
        assert limiter.get_remaining_requests("user1") == 2

    def test_reset_single_user(self):
        """Test resetting rate limit for single user."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)

        limiter.check_rate_limit("user1")
        limiter.check_rate_limit("user1")
        assert limiter.check_rate_limit("user1") is False

        limiter.reset("user1")
        assert limiter.check_rate_limit("user1") is True

    def test_reset_all_users(self):
        """Test resetting rate limit for all users."""
        limiter = RateLimiter(max_requests=1, window_seconds=1)

        limiter.check_rate_limit("user1")
        limiter.check_rate_limit("user2")

        limiter.reset()

        assert limiter.check_rate_limit("user1") is True
        assert limiter.check_rate_limit("user2") is True

    def test_rate_limit_decorator(self):
        """Test rate limit decorator."""
        @rate_limit(max_requests=3, window_seconds=1)
        def limited_function(user_id):
            return f"Called for {user_id}"

        # Should work for first 3 calls
        for _ in range(3):
            result = limited_function("user1")
            assert result == "Called for user1"

        # Should raise on 4th call
        with pytest.raises(RuntimeError, match="Rate limit exceeded"):
            limited_function("user1")


class TestSecurityAuditor:
    """Test cases for SecurityAuditor."""

    def test_safe_command(self):
        """Test audit of safe command."""
        auditor = SecurityAuditor()
        result = auditor.audit_command("@A:compress text")

        assert result['valid'] is True
        assert result['risk_level'] == "SAFE"
        assert result['risk_score'] < 20

    def test_dangerous_command(self):
        """Test audit of dangerous command."""
        auditor = SecurityAuditor()
        result = auditor.audit_command("@A:compress eval('code')")

        assert result['valid'] is False
        assert result['risk_level'] in ["HIGH", "CRITICAL"]
        assert len(result['errors']) > 0

    def test_complex_command(self):
        """Test audit of complex but valid command."""
        auditor = SecurityAuditor()
        complex_cmd = "@CMD[" * 5 + "param" + "]" * 5
        result = auditor.audit_command(complex_cmd)

        assert result['risk_score'] > 0
        # Should have some risk due to complexity

    def test_recommendations(self):
        """Test audit provides recommendations."""
        auditor = SecurityAuditor()
        result = auditor.audit_command("@A:compress eval('bad')")

        assert len(result['recommendations']) > 0
        assert any("Fix all validation errors" in rec for rec in result['recommendations'])


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_validate_command_function(self):
        """Test validate_command convenience function."""
        result = validate_command("@A:compress text")
        assert result.valid is True

    def test_audit_command_function(self):
        """Test audit_command convenience function."""
        result = audit_command("@A:compress text")
        assert result['valid'] is True
        assert 'risk_level' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
