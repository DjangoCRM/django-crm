"""Protocol and typing contracts shared across project apps."""

from typing import Protocol


class RawIdLabelDecorator(Protocol):
    """Decorate raw-id field labels on a ModelAdmin change/add form."""

    def __call__(self, admin_obj: object, form: object) -> None:
        """Apply label decoration for raw-id fields on the given form."""


class DashboardCounterProvider(Protocol):
    """Mutate dashboard model entries for an app on the admin index."""

    def __call__(self, request: object, models: list) -> None:
        """Apply counter badges to the model list for the current request."""


class HelpUrlProvider(Protocol):
    """Resolve contextual help URL for the current admin request."""

    def __call__(self, request: object) -> str:
        """Return a help page URL or an empty string when unavailable."""
