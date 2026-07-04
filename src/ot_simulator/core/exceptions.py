"""Custom exceptions for OT Simulator."""


class OTSimulatorError(Exception):
    """Base exception for all OT Simulator errors."""
    pass


class DataValidationError(OTSimulatorError):
    """Raised when a single record fails validation."""
    def __init__(self, message: str, field: str = None, value=None, row: int = None):
        self.field = field
        self.value = value
        self.row = row
        super().__init__(message)


class FileLoadError(OTSimulatorError):
    """Raised when a file cannot be read or parsed."""
    pass


class SchemaError(OTSimulatorError):
    """Raised when CSV columns don't match the expected schema."""
    def __init__(self, message: str, missing_columns: list = None, extra_columns: list = None):
        self.missing_columns = missing_columns or []
        self.extra_columns = extra_columns or []
        super().__init__(message)
