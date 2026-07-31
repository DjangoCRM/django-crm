"""Shared admin inlines without project-app dependencies."""

from __future__ import annotations

from django.contrib.contenttypes.admin import GenericStackedInline
from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe

from sharedkernel.presentation import SAFE_ATTACH_FILE_ICON

_FILE_INLINE_CLASS: type | None = None


def register_file_inline(cls: type) -> None:
    global _FILE_INLINE_CLASS
    if _FILE_INLINE_CLASS is not None and _FILE_INLINE_CLASS is not cls:
        raise ImproperlyConfigured('FileInline is already registered.')
    _FILE_INLINE_CLASS = cls


def get_file_inline_class() -> type:
    if _FILE_INLINE_CLASS is None:
        raise ImproperlyConfigured(
            'FileInline is not registered; ensure the common app has loaded.',
        )
    return _FILE_INLINE_CLASS


def __getattr__(name: str):
    if name == 'FileInline':
        return get_file_inline_class()
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


class BaseFileInline(GenericStackedInline):
    """Generic file attachment inline; subclasses bind model and form."""

    extra = 0
    fields = ('file',)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if getattr(cls, 'model', None) is not None:
            icon = getattr(cls, 'icon', SAFE_ATTACH_FILE_ICON)
            name_plural = cls.model._meta.verbose_name_plural
            cls.verbose_name_plural = mark_safe(f'{icon} {name_plural}')

    # -- GenericStackedInline methods -- #

    def has_add_permission(self, request, obj):
        # for memos only the recipient can add files until the memo is reviewed
        if hasattr(obj, 'REVIEWED') and obj.stage != obj.REVIEWED:
            if obj.to == request.user:
                return True
        # who can change a parent object should
        # have permission to add inline
        return self.has_change_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        value = super().has_change_permission(request, obj)
        if not value or not obj:
            return value
        return self.clarify_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # who can change a parent object should
        # have permission to delete inline
        return self.has_change_permission(request, obj)

    # -- Custom methods -- #

    @staticmethod
    def clarify_permission(request, obj):
        # Intentionally not unified with other permission helpers (see WO-035).
        if hasattr(obj, 'owner'):
            if obj.owner == request.user or not obj.owner:
                if any((hasattr(obj, 'REVIEWED') and obj.stage == obj.REVIEWED,
                        hasattr(obj, 'incoming') and obj.incoming,
                        hasattr(obj, 'uid') and obj.uid,
                        not obj.owner and request.user.is_chief)):
                    return False
                return True
        else:
            return True

        if hasattr(obj, 'co_owner') and obj.co_owner == request.user \
                or request.user.is_superoperator \
                or request.user.is_task_operator \
                or request.user.is_superuser \
                or hasattr(obj, 'department') and request.user.is_operator \
                and obj.department_id == request.user.department_id \
                or hasattr(obj, 'responsible') and obj.responsible.count() == 1 \
                and request.user in (obj.responsible.all()) \
                or hasattr(obj, 'win_closing_date') and request.user.is_chief:
            return True

        return False
