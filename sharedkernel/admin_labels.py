"""Neutral admin label helpers without project-app dependencies."""


def noop_raw_id_label_decorator(admin_obj, form) -> None:
    """Default hook: leave raw-id field labels unchanged."""


def append_id_to_raw_id_field_labels(admin_obj, form) -> None:
    """Append ', ID' to raw-id foreign-key field labels."""
    for field in admin_obj.raw_id_fields:
        if field in form.base_fields:
            label = form.base_fields[field].label
            form.base_fields[field].label = f"{label}, ID"
