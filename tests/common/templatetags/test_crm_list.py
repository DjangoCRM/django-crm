from django.contrib.admin.views.main import PAGE_VAR
from django.test import tag
from django.test import TestCase
from django.core.paginator import Paginator
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from common.templatetags.crm_list import DOT
from common.templatetags.crm_list import get_query_string
from common.templatetags.crm_list import pagination
from common.templatetags.crm_list import paginator_number
from common.templatetags.crm_list import ON_EACH_SIDE
from common.templatetags.crm_list import ON_ENDS

# manage.py test tests.common.templatetags.test_crm_list --keepdb


@tag('TestCase')
class TestsCrmList(TestCase):

    def setUp(self):
        print("Run Test Method:", self._testMethodName)

    def test_pagination_num_pages_less_10(self):
        per_page = 2
        objects = [f'O{i}' for i in range(0, 9)]
        p = Paginator(objects, per_page)
        num_objects = len(objects)
        stop = int(num_objects/per_page)
        if num_objects % per_page != 0:
            stop += 1
        page_num = 1
        page = p.page(page_num)
        page.page_num = page_num
        data = pagination(page)
        # print(data['page_range'])
        self.assertEqual(range(0, stop), data['page_range'])

    def test_pagination_num_pages_15(self):
        num_pages = 15
        per_page = 2
        page_num = ON_EACH_SIDE + ON_ENDS + 1
        rng = range(0, num_pages * per_page)
        objects = [f'O{i}' for i in rng]
        page_range = get_page_range(objects, per_page, page_num)
        expected_page_range = [
            *range(0, ON_ENDS), DOT,
            *range(page_num - ON_EACH_SIDE, page_num + 1),
        ]
        expected_page_range += [
            *range(page_num + 1, page_num + ON_EACH_SIDE + 1), DOT,
            *range(num_pages - ON_ENDS, num_pages)
        ]
        # print(data['page_range'])
        self.assertEqual(expected_page_range, page_range)

        page_num = ON_EACH_SIDE + ON_ENDS - 1
        page_range = get_page_range(objects, per_page, page_num)
        expected_page_range = []
        expected_page_range.extend(range(0, page_num + 1))
        expected_page_range += [
            *range(page_num + 1, page_num + ON_EACH_SIDE + 1), DOT,
            *range(num_pages - ON_ENDS, num_pages)
        ]
        self.assertEqual(expected_page_range, page_range)

        page_num = num_pages - ON_EACH_SIDE - ON_ENDS
        page_range = get_page_range(objects, per_page, page_num)
        expected_page_range = [
            *range(0, ON_ENDS), DOT,
            *range(page_num - ON_EACH_SIDE, page_num + 1),
        ]
        expected_page_range.extend(range(page_num + 1, num_pages))
        self.assertEqual(expected_page_range, page_range)

    def test_paginator_number_i_DOT(self):
        page = ''
        i = DOT
        self.assertEqual('… ', paginator_number(page, i))

    def test_paginator_number_i_page_num(self):
        per_page = 2
        objects = [f'O{i}' for i in range(0, 9)]
        p = Paginator(objects, per_page)
        page_num = i = 1
        page = p.page(page_num)
        page.page_num = page_num
        self.assertEqual(
            format_html('<span class="this-page">{}</span> ', i + 1),
            paginator_number(page, i)
        )

    def test_paginator_number_i_not_page_num(self):
        per_page = 2
        objects = [f'O{i}' for i in range(0, 9)]
        p = Paginator(objects, per_page)
        i = 1
        page_num = 2
        page = p.page(page_num)
        page.page_num = page_num
        page.params = {'p': '1'}
        expected = format_html(
            '<a href="{}"{}>{}</a> ',
            get_query_string(page, {PAGE_VAR: i}),
            mark_safe(' class="end"' if i == page.paginator.num_pages - 1 else ''),
            i + 1,
        )
        self.assertEqual(expected, paginator_number(page, i))


def get_page_range(objects, per_page, page_num):
    p = Paginator(objects, per_page)
    page = p.page(page_num)
    page.page_num = page_num
    return pagination(page)['page_range']
