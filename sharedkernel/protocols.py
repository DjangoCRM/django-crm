"""Protocol and typing contracts shared across project apps."""

from typing import Protocol


class RawIdLabelDecorator(Protocol):
    """Decorate raw-id field labels on a ModelAdmin change/add form."""

    def __call__(self, admin_obj: object, form: object) -> None:
        """Apply label decoration for raw-id fields on the given form."""
