"""Soul system error hierarchy — modeled after MarkItDown's exception design."""


class SoulException(Exception):
    """Base exception for all soul system errors."""
    pass


class SoulBackendError(SoulException):
    """Raised when a backend operation fails."""
    pass


class SoulStateError(SoulException):
    """Raised when soul state is invalid or missing."""
    pass


class SoulPluginError(SoulException):
    """Raised when a plugin fails to load or register."""
    pass


class SoulVersionMismatch(SoulException):
    """Raised when soul data was written by a different/incompatible version."""
    pass
