# ADR: Legacy `common.utils.helpers` deprecation shim

## Status

Accepted

## Context

Presentation constants, ORM query helpers, and workflow utilities were relocated to
`sharedkernel.presentation`, `common.queries`, and `common.services.*` during the
layering epic (WO-028 through WO-030). Forks, plugins, and many internal modules
still import the old `common.utils.helpers` paths.

## Decision

Keep `common/utils/helpers.py` as a thin compatibility shim until release **3.0.0**.
Moved symbols are resolved lazily through a module-level `__getattr__` hook that:

- emits a `DeprecationWarning` naming the old path, new path, and removal release
- warns at most once per symbol per process
- caches resolved objects for subsequent access

Importing `common.utils.helpers` alone is silent. `USER_MODEL` remains a direct
module attribute because it was not relocated.

## Symbol mapping

| Legacy import | Canonical import |
| --- | --- |
| `common.utils.helpers.add_chat_context` | `common.queries.add_chat_context` |
| `common.utils.helpers.add_phone_q_params` | `common.queries.add_phone_q_params` |
| `common.utils.helpers.annotate_chat` | `common.queries.annotate_chat` |
| `common.utils.helpers.get_active_users` | `common.queries.get_active_users` |
| `common.utils.helpers.get_department_id` | `common.queries.get_department_id` |
| `common.utils.helpers.get_manager_departments` | `common.queries.get_manager_departments` |
| `common.utils.helpers.CONTENT_COPY_ICON` | `sharedkernel.presentation.CONTENT_COPY_ICON` |
| `common.utils.helpers.CONTENT_COPY_LINK` | `sharedkernel.presentation.CONTENT_COPY_LINK` |
| `common.utils.helpers.COPY_STR` | `sharedkernel.presentation.COPY_STR` |
| `common.utils.helpers.CRM_NOTICE` | `sharedkernel.presentation.CRM_NOTICE` |
| `common.utils.helpers.FRIDAY_SATURDAY_SUNDAY_MSG` | `sharedkernel.presentation.FRIDAY_SATURDAY_SUNDAY_MSG` |
| `common.utils.helpers.LEADERS` | `sharedkernel.presentation.LEADERS` |
| `common.utils.helpers.OBJ_DOESNT_EXIT_STR` | `sharedkernel.presentation.OBJ_DOESNT_EXIT_STR` |
| `common.utils.helpers.ONCLICK_STR` | `sharedkernel.presentation.ONCLICK_STR` |
| `common.utils.helpers.SAFE_ATTACH_FILE_ICON` | `sharedkernel.presentation.SAFE_ATTACH_FILE_ICON` |
| `common.utils.helpers.SAFE_SUBJECT_ICON` | `sharedkernel.presentation.SAFE_SUBJECT_ICON` |
| `common.utils.helpers.get_formatted_short_date` | `sharedkernel.presentation.get_formatted_short_date` |
| `common.utils.helpers.get_verbose_name` | `sharedkernel.presentation.get_verbose_name` |
| `common.utils.helpers.popup_window` | `sharedkernel.presentation.popup_window` |
| `common.utils.helpers.compose_message` | `common.services.messaging.compose_message` |
| `common.utils.helpers.compose_subject` | `common.services.messaging.compose_subject` |
| `common.utils.helpers.get_delta_date` | `common.services.datetimes.get_delta_date` |
| `common.utils.helpers.get_now` | `common.services.datetimes.get_now` |
| `common.utils.helpers.get_today` | `common.services.datetimes.get_today` |
| `common.utils.helpers.notify_admins_no_email` | `common.services.notifications.notify_admins_no_email` |
| `common.utils.helpers.save_message` | `common.services.notifications.save_message` |
| `common.utils.helpers.send_crm_email` | `common.services.notifications.send_crm_email` |
| `common.utils.helpers.set_toggle_tooltip` | `common.services.notifications.set_toggle_tooltip` |
| `common.utils.helpers.token_default` | `common.services.tokens.token_default` |
| `common.utils.helpers.get_trans_for_lang` | `common.services.translations.get_trans_for_lang` |
| `common.utils.helpers.get_trans_for_user` | `common.services.translations.get_trans_for_user` |
| `common.utils.helpers.get_user_language_code` | `common.services.translations.get_user_language_code` |

## Consequences

- Internal call sites should migrate to canonical imports (WO-033).
- Running tests with shim warnings escalated to errors surfaces remaining legacy usage.
- The shim is removed entirely in 3.0.0 after fan-in reaches zero.
