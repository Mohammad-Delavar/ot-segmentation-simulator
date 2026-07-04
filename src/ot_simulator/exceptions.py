"""Custom exception hierarchy for the OT Simulator."""
from __future__ import annotations


class OTSimulatorError(Exception):
    """Base exception for all OT Simulator errors."""


class DataLoadError(OTSimulatorError):
    """Raised when input data cannot be loaded or parsed."""


class FileNotFoundError_(DataLoadError):
    """Raised when an expected input file is missing."""


class SchemaError(DataLoadError):
    """Raised when a CSV is missing required columns."""


class ValidationError(DataLoadError):
    """Raised when a row fails validation in strict mode."""

    def __init__(self, message: str, *, source: str, row: int) -> None:
        self.source = source
        self.row = row
        super().__init__(f"[{source}:row {row}] {message}")
