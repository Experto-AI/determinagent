"""
Unified exception hierarchy for DeterminAgent.

All CLI-specific errors are normalized to these exceptions,
providing a consistent interface for error handling.
"""


class DeterminAgentError(Exception):
    """Base exception for all DeterminAgent errors."""

    def __init__(self, message: str, provider: str | None = None) -> None:
        self.message = message
        self.provider = provider
        super().__init__(message)


# ============================================================================
# Provider Availability Errors
# ============================================================================


class ProviderNotAvailable(DeterminAgentError):
    """
    Raised when a CLI provider is not installed or not accessible.

    Examples:
        - "claude: command not found"
        - "gemini: not installed"
    """

    pass


class ProviderAuthError(DeterminAgentError):
    """
    Raised when authentication fails for a provider.

    Examples:
        - Missing API key
        - Invalid credentials
        - Expired token
    """

    pass


# ============================================================================
# Rate Limiting & Quota Errors
# ============================================================================


class RateLimitExceeded(DeterminAgentError):
    """
    Raised when API rate limits are exceeded.

    Attributes:
        retry_after: Suggested wait time in seconds (if available)
    """

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, provider)
        self.retry_after = retry_after


class QuotaExceeded(DeterminAgentError):
    """
    Raised when usage quota is exceeded (e.g., monthly limits).
    """

    pass


# ============================================================================
# Execution Errors
# ============================================================================


class ExecutionError(DeterminAgentError):
    """
    Raised when CLI command execution fails.

    Attributes:
        returncode: Process exit code
        stderr: Standard error output
    """

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        returncode: int | None = None,
        stderr: str | None = None,
    ) -> None:
        super().__init__(message, provider)
        self.returncode = returncode
        self.stderr = stderr


class TimeoutError(ExecutionError):
    """
    Raised when CLI command times out.

    Attributes:
        timeout: The timeout value that was exceeded (in seconds)
    """

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        timeout: int | None = None,
    ) -> None:
        super().__init__(message, provider)
        self.timeout = timeout


class SandboxViolation(ExecutionError):
    """
    Raised when an operation is blocked by sandbox restrictions.

    Codex-specific: Operation blocked by sandbox policy.
    """

    pass


# ============================================================================
# Parsing & Validation Errors
# ============================================================================


class ParseError(DeterminAgentError):
    """
    Raised when response parsing fails.

    Examples:
        - Invalid JSON from provider
        - Unexpected output format
    """

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        raw_output: str | None = None,
    ) -> None:
        super().__init__(message, provider)
        self.raw_output = raw_output


class ValidationError(DeterminAgentError):
    """
    Raised when output validation fails.

    Examples:
        - Pydantic validation failure
        - Schema mismatch
    """

    pass


# ============================================================================
# Session Errors
# ============================================================================


class SessionError(DeterminAgentError):
    """
    Raised when session management fails.

    Examples:
        - Session not found
        - Session expired
        - Invalid session ID
    """

    pass


# ============================================================================
# Configuration Errors
# ============================================================================


class ConfigurationError(DeterminAgentError):
    """
    Raised when configuration is invalid or missing.

    Examples:
        - Invalid YAML syntax
        - Missing required fields
        - Invalid model alias
    """

    pass
