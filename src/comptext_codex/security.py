"""Security and validation utilities for CompText-Codex.

Provides input validation, sanitization, rate limiting, and security features
to ensure safe and stable operation.
"""

import re
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from functools import wraps
import hashlib


@dataclass
class ValidationResult:
    """Result of input validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sanitized_input: Optional[str] = None


class InputValidator:
    """Validates and sanitizes CompText commands."""

    # Maximum command length (prevent DoS)
    MAX_COMMAND_LENGTH = 10000

    # Maximum nesting depth for brackets
    MAX_BRACKET_DEPTH = 10

    # Maximum number of chained commands
    MAX_CHAINED_COMMANDS = 20

    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'__\w+__',  # Python dunder methods
        r'eval\s*\(',  # eval() calls
        r'exec\s*\(',  # exec() calls
        r'import\s+',  # import statements
        r'from\s+\w+\s+import',  # from...import statements
        r'os\.',  # os module access
        r'sys\.',  # sys module access
        r'subprocess\.',  # subprocess module
        r'open\s*\(',  # file operations
        r'file\s*\(',  # file operations
    ]

    # Allowed command pattern
    VALID_COMMAND_PATTERN = re.compile(
        r'^@[A-M]:\w+\s.*$|^@\w+\[[^\]]*\]$|^@[A-M]:\w+$',
        re.DOTALL
    )

    def validate(self, command: str) -> ValidationResult:
        """Validate a CompText command.

        Args:
            command: Command string to validate

        Returns:
            ValidationResult with validation status and errors
        """
        errors = []
        warnings = []

        # Check length
        if len(command) > self.MAX_COMMAND_LENGTH:
            errors.append(
                f"Command exceeds maximum length ({self.MAX_COMMAND_LENGTH} chars)"
            )

        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                errors.append(
                    f"Command contains potentially dangerous pattern: {pattern}"
                )

        # Check bracket depth
        depth = self._check_bracket_depth(command)
        if depth > self.MAX_BRACKET_DEPTH:
            errors.append(
                f"Bracket nesting depth ({depth}) exceeds maximum ({self.MAX_BRACKET_DEPTH})"
            )

        # Check number of chained commands
        chain_count = command.count('+') + 1
        if chain_count > self.MAX_CHAINED_COMMANDS:
            errors.append(
                f"Too many chained commands ({chain_count} > {self.MAX_CHAINED_COMMANDS})"
            )

        # Check for balanced brackets
        if not self._check_balanced_brackets(command):
            errors.append("Unbalanced brackets in command")

        # Check for null bytes
        if '\x00' in command:
            errors.append("Command contains null bytes")

        # Sanitize input
        sanitized = self._sanitize(command)

        # Warn if sanitization changed the input
        if sanitized != command:
            warnings.append("Input was sanitized")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_input=sanitized
        )

    def _check_bracket_depth(self, text: str) -> int:
        """Check maximum bracket nesting depth."""
        max_depth = 0
        current_depth = 0

        for char in text:
            if char == '[':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == ']':
                current_depth -= 1

        return max_depth

    def _check_balanced_brackets(self, text: str) -> bool:
        """Check if brackets are balanced."""
        stack = []
        pairs = {'[': ']', '(': ')', '{': '}'}

        for char in text:
            if char in pairs.keys():
                stack.append(char)
            elif char in pairs.values():
                if not stack:
                    return False
                if pairs[stack.pop()] != char:
                    return False

        return len(stack) == 0

    def _sanitize(self, command: str) -> str:
        """Sanitize command input.

        Args:
            command: Command to sanitize

        Returns:
            Sanitized command
        """
        # Remove null bytes
        sanitized = command.replace('\x00', '')

        # Remove control characters (except newlines and tabs)
        sanitized = ''.join(
            char for char in sanitized
            if char.isprintable() or char in '\n\t'
        )

        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())

        return sanitized


class RateLimiter:
    """Rate limiter to prevent abuse."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = {}

    def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limit.

        Args:
            identifier: Unique identifier (e.g., user ID, IP)

        Returns:
            True if allowed, False if rate limited
        """
        now = time.time()

        # Get request history for this identifier
        if identifier not in self._requests:
            self._requests[identifier] = []

        # Remove old requests outside the window
        cutoff = now - self.window_seconds
        self._requests[identifier] = [
            timestamp for timestamp in self._requests[identifier]
            if timestamp > cutoff
        ]

        # Check if under limit
        if len(self._requests[identifier]) >= self.max_requests:
            return False

        # Add current request
        self._requests[identifier].append(now)
        return True

    def get_remaining_requests(self, identifier: str) -> int:
        """Get number of remaining requests for identifier.

        Args:
            identifier: Unique identifier

        Returns:
            Number of remaining requests
        """
        if identifier not in self._requests:
            return self.max_requests

        now = time.time()
        cutoff = now - self.window_seconds

        valid_requests = [
            timestamp for timestamp in self._requests[identifier]
            if timestamp > cutoff
        ]

        return max(0, self.max_requests - len(valid_requests))

    def reset(self, identifier: Optional[str] = None):
        """Reset rate limit for identifier or all.

        Args:
            identifier: Optional identifier to reset (None = reset all)
        """
        if identifier:
            self._requests.pop(identifier, None)
        else:
            self._requests.clear()


def rate_limit(max_requests: int = 100, window_seconds: int = 60):
    """Decorator for rate limiting functions.

    Args:
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds

    Returns:
        Decorated function

    Example:
        @rate_limit(max_requests=10, window_seconds=60)
        def my_function(user_id):
            pass
    """
    limiter = RateLimiter(max_requests, window_seconds)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use first argument as identifier
            identifier = str(args[0]) if args else "default"

            if not limiter.check_rate_limit(identifier):
                raise RuntimeError(
                    f"Rate limit exceeded: {max_requests} requests per {window_seconds}s"
                )

            return func(*args, **kwargs)

        wrapper.limiter = limiter
        return wrapper

    return decorator


class SecurityAuditor:
    """Audits commands for security issues."""

    def __init__(self):
        """Initialize security auditor."""
        self.validator = InputValidator()

    def audit_command(self, command: str) -> Dict[str, Any]:
        """Audit a command for security issues.

        Args:
            command: Command to audit

        Returns:
            Audit result dictionary
        """
        validation = self.validator.validate(command)

        # Calculate risk score
        risk_score = self._calculate_risk_score(command, validation)

        # Determine risk level
        if risk_score >= 80:
            risk_level = "CRITICAL"
        elif risk_score >= 60:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        elif risk_score >= 20:
            risk_level = "LOW"
        else:
            risk_level = "SAFE"

        return {
            'valid': validation.valid,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'errors': validation.errors,
            'warnings': validation.warnings,
            'recommendations': self._get_recommendations(validation, risk_score)
        }

    def _calculate_risk_score(self, command: str, validation: ValidationResult) -> int:
        """Calculate risk score (0-100)."""
        score = 0

        # Check for dangerous patterns first (highest risk)
        for pattern in self.validator.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                score += 50  # Very high risk for dangerous patterns

        # Base score for errors
        score += len(validation.errors) * 20

        # Warnings add moderate risk
        score += len(validation.warnings) * 10

        # Length adds minor risk
        if len(command) > 1000:
            score += 5

        # Complexity adds risk
        bracket_depth = self.validator._check_bracket_depth(command)
        score += min(bracket_depth * 5, 20)

        # Chaining adds minor risk
        chain_count = command.count('+')
        score += min(chain_count * 2, 10)

        return min(score, 100)

    def _get_recommendations(self, validation: ValidationResult, risk_score: int) -> List[str]:
        """Get security recommendations."""
        recommendations = []

        if risk_score >= 60:
            recommendations.append("Review and simplify command structure")

        if validation.errors:
            recommendations.append("Fix all validation errors before execution")

        if validation.warnings:
            recommendations.append("Review warnings and ensure expected behavior")

        return recommendations


# Global instances
_validator = InputValidator()
_auditor = SecurityAuditor()


def validate_command(command: str) -> ValidationResult:
    """Validate a CompText command (convenience function).

    Args:
        command: Command to validate

    Returns:
        ValidationResult
    """
    return _validator.validate(command)


def audit_command(command: str) -> Dict[str, Any]:
    """Audit a command for security (convenience function).

    Args:
        command: Command to audit

    Returns:
        Audit result dictionary
    """
    return _auditor.audit_command(command)
