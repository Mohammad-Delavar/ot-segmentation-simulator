"""Result aggregation for load operations."""

from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class LoadError:
    """A single error encountered during loading."""
    row: int | None
    message: str
    field: str | None = None
    value: object = None

    def __str__(self) -> str:
        loc = f"row {self.row}" if self.row is not None else "file"
        fld = f" [{self.field}={self.value!r}]" if self.field else ""
        return f"{loc}{fld}: {self.message}"


@dataclass
class LoadResult(Generic[T]):
    """Aggregated result of a load operation.

    Holds successfully parsed items plus any errors/warnings,
    so the loader never silently swallows bad rows.
    """
    items: list[T] = field(default_factory=list)
    errors: list[LoadError] = field(default_factory=list)
    warnings: list[LoadError] = field(default_factory=list)
    total_rows: int = 0

    @property
    def loaded_count(self) -> int:
        return len(self.items)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def is_ok(self) -> bool:
        return not self.errors

    def add_error(self, row, message, field=None, value=None):
        self.errors.append(LoadError(row, message, field, value))

    def add_warning(self, row, message, field=None, value=None):
        self.warnings.append(LoadError(row, message, field, value))

    def summary(self) -> str:
        return (
            f"loaded {self.loaded_count}/{self.total_rows} "
            f"({self.error_count} errors, {len(self.warnings)} warnings)"
        )
