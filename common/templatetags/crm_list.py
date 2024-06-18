from django.contrib.admin.views.main import PAGE_VAR
from django.template import Library
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.http import urlencode
from django.contrib.admin.templatetags.base import InclusionAdminNode


register = Library()

DOT = '.'
ON_EACH_SIDE = 3
ON_ENDS = 2


@register.simple_tag
def paginator_number(page, i):
    """
    Generate an individual page index link in a paginated list.
    """
    if i == DOT:
        return '… '
    elif i == page.page_num:
        return format_html('<span class="this-page">{}</span> ', i + 1)
    else:
        return format_html(
            '<a href="{}"{}>{}</a> ',
            get_query_string(page, {PAGE_VAR: i}),
            mark_safe(' class="end"' if i == page.paginator.num_pages - 1 else ''),
            i + 1,
        )


def pagination(page):
    """
    Generate the series of links to the pages in a paginated list.
    """
    paginator, page_num = page.paginator, page.page_num

    page_range = []
    # If there are 10 or fewer pages, display links to every page.
    # Otherwise, do some fancy
    if paginator.num_pages <= 10:
        page_range = range(paginator.num_pages)
    else:
        # Insert "smart" pagination links, so that there are always ON_ENDS
        # links at either end of the list of pages, and there are always
        # ON_EACH_SIDE links at either end of the "current page" link.
        if page_num > (ON_EACH_SIDE + ON_ENDS):
            page_range += [
                *range(0, ON_ENDS), DOT,
                *range(page_num - ON_EACH_SIDE, page_num + 1),
            ]
        else:
            page_range.extend(range(0, page_num + 1))
        if page_num < (paginator.num_pages - ON_EACH_SIDE - ON_ENDS - 1):
            page_range += [
                *range(page_num + 1, page_num + ON_EACH_SIDE + 1), DOT,
                *range(paginator.num_pages - ON_ENDS, paginator.num_pages)
            ]
        else:
            page_range.extend(range(page_num + 1, paginator.num_pages))
    return {
        'page': page,
        'page_range': page_range,
        '1': 1,
    }


@register.tag(name='pagination')
def pagination_tag(parser, token):
    return InclusionAdminNode(
        parser, token,
        func=pagination,
        template_name='/common/import_emails/pagination.html',
        takes_context=False,
    )


def get_query_string(page, new_params=None):
    if new_params is None:
        new_params = {}
    p = page.params.copy()
    for k, v in new_params.items():
        if v is None:
            if k in p:
                del p[k]
        else:
            p[k] = v
    return '?%s' % urlencode(sorted(p.items()))
