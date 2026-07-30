from decimal import Decimal
from dateutil.relativedelta import relativedelta
from typing import Tuple
from django.db.models import Aggregate
from django.db.models import CharField
from django.db.models import TextField
from django.db.models.functions import Cast
from django.db.models.functions import Trunc
from django.db.models import Count
from django.db.models import Case
from django.db.models import DecimalField
from django.db.models import Exists
from django.db.models import F
from django.db.models import Max
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models import Subquery
from django.db.models import Sum
from django.db.models import When
from django.db.utils import NotSupportedError
from django.core.handlers.wsgi import WSGIRequest

from common.services.datetimes import get_today
from crm.models import Currency
from crm.models import Rate


class GroupConcat(Aggregate):
    """
    Database-portable string aggregation.

    Compiles to GROUP_CONCAT on MySQL, STRING_AGG on PostgreSQL, and
    group_concat on SQLite while preserving equivalent semantics.
    """

    function = 'GROUP_CONCAT'
    allow_distinct = True

    def __init__(self, expression, distinct=False, ordering=None, separator=', ', **extra):
        self.ordering = ordering
        self.separator = separator
        super().__init__(
            expression,
            distinct=distinct,
            output_field=CharField(),
            **extra
        )

    def _compile_source(self, compiler, connection):
        return compiler.compile(self.source_expressions[0])

    def _ordering_sql(self, compiler, connection):
        if self.ordering is None:
            return '', []
        order_sql, order_params = compiler.compile(self.ordering)
        return f' ORDER BY {order_sql}', order_params

    def as_mysql(self, compiler, connection, **extra_context):
        sql, params = self._compile_source(compiler, connection)
        distinct_sql = 'DISTINCT ' if self.distinct else ''
        ordering_sql, ordering_params = self._ordering_sql(compiler, connection)
        return (
            f'GROUP_CONCAT({distinct_sql}{sql}{ordering_sql} SEPARATOR %s)',
            params + ordering_params + (self.separator,),
        )

    def as_postgresql(self, compiler, connection, **extra_context):
        cast_expr = Cast(self.source_expressions[0], output_field=TextField())
        sql, params = compiler.compile(cast_expr)
        distinct_sql = 'DISTINCT ' if self.distinct else ''
        ordering_sql, ordering_params = self._ordering_sql(compiler, connection)
        return (
            f'STRING_AGG({distinct_sql}{sql}{ordering_sql}, %s)',
            params + ordering_params + (self.separator,),
        )

    def as_sqlite(self, compiler, connection, **extra_context):
        if self.distinct and self.separator != ',':
            raise NotSupportedError(
                'GroupConcat does not support DISTINCT with a custom separator '
                'on SQLite; use the default comma separator or omit DISTINCT.'
            )
        sql, params = self._compile_source(compiler, connection)
        if self.distinct:
            return f'group_concat(DISTINCT {sql})', params
        return f'group_concat({sql}, %s)', params + (self.separator,)


def get_currency_info(request: WSGIRequest) -> Tuple[str, str, str]:
    currencies = Currency.objects.filter(
        Q(is_marketing_currency=True) | Q(is_state_currency=True)
    )
    try:
        marketing_currency = currencies.get(is_marketing_currency=True)
    except Currency.DoesNotExist:
        marketing_currency = Currency.objects.first()

    try:
        state_currency = currencies.get(is_state_currency=True)
    except Currency.DoesNotExist:
        state_currency = Currency.objects.first()

    rate_field_name = request.session.get('rate_field_name', 'rate_to_marketing_currency')
    button_title = f"{marketing_currency.name} > {state_currency.name}"
    if rate_field_name == 'rate_to_marketing_currency':
        current_currency = marketing_currency
    else:
        current_currency = state_currency
        button_title = f"{state_currency.name} > {marketing_currency.name}"
    if marketing_currency == state_currency:
        button_title = ''
    return current_currency.name, rate_field_name, button_title


def get_current_currency_amount(payment_queryset: QuerySet,
                                rate_field_name: str) -> Tuple[QuerySet, Decimal]:
    rate = Rate.objects.filter(
        currency=OuterRef('currency'),
        payment_date=OuterRef('payment_date')
    )
    payment_queryset = payment_queryset.annotate(
        value=get_amount_in_currency(rate, rate_field_name)
    )     
    total_data = payment_queryset.aggregate(amount=Sum('value'))
    sta = total_data['amount']
    return payment_queryset, round(sta, 2) if sta else 0


def get_values_over_time(queryset: QuerySet, field: str) -> tuple:
    values = queryset.annotate(
        period=Trunc(field, 'month')
    ).values('period').annotate(
        total=Count('id')
    ).order_by('period')
    return check_time_periods(values), get_maximum(values)


def get_income_over_time(payment_queryset: QuerySet, field: str,
                         rate_field_name: str, earliest_date=None) -> tuple:
    rate = Rate.objects.filter(
        currency=OuterRef('currency'),
        payment_date=OuterRef('payment_date')
    )
    values = payment_queryset.annotate(
        period=Trunc(field, 'month')
    ).values('period').annotate(
        total=Sum(
            get_amount_in_currency(rate, rate_field_name)
        )
    ).order_by('period')
    return check_time_periods(values, earliest_date), get_maximum(values)


def get_amount_in_currency(rate, rate_field_name):
    return Case(
        When(Exists(rate),
             then=F('amount') * Subquery(rate.values(rate_field_name)[:1]),),
        default=F('amount') * F(f'currency__{rate_field_name}'),
        output_field=DecimalField()
    )


def get_maximum(values):
    value = values.aggregate(
        high=Max('total'),
    ).get('high', 0)
    return value or 0


def check_time_periods(queryset: QuerySet, earliest_date=None) -> list:
    earliest_date = earliest_date or get_today()
    date = earliest_date.replace(day=1) + relativedelta(months=-11)
    return get_item_list(queryset, date)


def get_item_list(queryset: QuerySet, date) -> list:
    item_list = list(queryset)
    if item_list and item_list[0]['period'] < date:
        item_list.pop(0)
    for i in range(0, 12):
        item = next((
            item for item in item_list
            if item["period"] == date
        ), None)
        if not item:
            item_list.insert(i, {'period': date, 'total': 0})
        date = date + relativedelta(months=1)
    return item_list
