"""Domain-specific exceptions for business logic errors."""


class DomainException(Exception):
    """Base exception for all domain-related errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class NotFoundError(DomainException):
    """Raised when a requested resource is not found.

    Maps to HTTP 404 Not Found.
    """

    def __init__(self, resource: str, identifier: int | str) -> None:
        self.resource = resource
        self.identifier = identifier
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message)


class ValidationError(DomainException):
    """Raised when business rule validation fails.

    Maps to HTTP 400 Bad Request.
    Examples: empty title, invalid state transition.
    """

    pass


class ConflictError(DomainException):
    """Raised when a unique constraint would be violated.

    Maps to HTTP 409 Conflict.
    Examples: duplicate slug.
    """

    pass
