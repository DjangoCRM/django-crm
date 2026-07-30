"""Deterministic payment rows for GroupConcat aggregate tests."""

import json
from datetime import date
from pathlib import Path

from crm.models import Payment

_FIXTURE_PATH = Path(__file__).resolve().parent / 'group_concat_payments.json'
with _FIXTURE_PATH.open(encoding='utf-8') as fixture_file:
    _FIXTURE_DATA = json.load(fixture_file)

GROUP_CONCAT_ORDER_NUMBERS = tuple(_FIXTURE_DATA['order_numbers'])
GROUP_CONCAT_SEPARATOR = _FIXTURE_DATA['separator']


def seed_group_concat_payments(
    deal,
    currency,
    order_numbers=GROUP_CONCAT_ORDER_NUMBERS,
    status=Payment.RECEIVED,
):
    """
    Create payments with known order numbers for one deal.

    Returns the list of Payment instances in creation order.
    """
    payments = []
    for index, order_number in enumerate(order_numbers):
        payments.append(
            Payment.objects.create(
                deal=deal,
                status=status,
                amount=100 + index,
                currency=currency,
                payment_date=date.today(),
                order_number=order_number,
            )
        )
    return payments
