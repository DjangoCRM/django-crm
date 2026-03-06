from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


DOWNLOAD_ICON = '<i class="material-icons" ' \
                'style="font-size:17px;vertical-align:middle;">file_download</i> '
RED_DOWNLOAD_ICON = '<i class="material-icons" ' \
                    'style="font-size:17px;vertical-align:middle;color: var(--error-fg);">file_download</i>'
ERROR_OUTLINE_ICON = '<i class="material-icons" ' \
                     'style="font-size:17px;vertical-align:middle;color: var(--error-fg)">error_outline</i>'
FILE_ERROR = f'<span style="color: var(--error-fg)">{_("Error: the file is missing.")}</span>'


def get_file_links(files: QuerySet) -> mark_safe:
    """Generate HTML links for downloading files."""
    file_links = ''
    for f in files:
        file = getattr(f, 'file', None)
        if file:
            file_links += f'{DOWNLOAD_ICON} <a href="{file.url}">{f}</a><br>'
        else:
            file_links += f'{RED_DOWNLOAD_ICON}{ERROR_OUTLINE_ICON} {FILE_ERROR}<br>'
    return mark_safe(file_links)  # NOQA
