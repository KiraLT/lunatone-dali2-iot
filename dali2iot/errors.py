"""Exceptions raised by the Lunatone Dali-2 IoT client."""


class DaliIotError(Exception):
    """Base class for every error this package raises.

    Catch this if you want to handle any failure originating from the
    client (currently just :class:`ApiError`, but reserved for future
    transport / decoding errors).
    """


class ApiError(DaliIotError):
    """Raised when the gateway returns a non-2xx HTTP status.

    Attributes:
        status_code: HTTP status code returned by the gateway.
        content: Raw response body (bytes) for diagnostics.
    """

    def __init__(self, status_code: int, content: bytes):
        self.status_code = status_code
        """HTTP status code returned by the gateway."""

        self.content = content
        """Raw response body, useful for inspecting validation errors."""

        super().__init__(f"HTTP {status_code}: {content.decode(errors='ignore')}")


__all__ = ["ApiError", "DaliIotError"]
