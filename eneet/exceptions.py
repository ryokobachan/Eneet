"""Custom exceptions for Eneet."""


class EneetError(Exception):
    """Base exception for all Eneet errors."""
    pass


class UserNotFoundError(EneetError):
    """Raised when a user is not found on Nitter."""
    pass


class FetchError(EneetError):
    """Raised when there's an error fetching data from Nitter."""
    pass


class ParseError(EneetError):
    """Raised when there's an error parsing Nitter HTML."""
    pass
