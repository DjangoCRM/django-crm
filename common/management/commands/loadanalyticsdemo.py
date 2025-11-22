from __future__ import annotations

from datetime import timedelta
import random

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

class Command(BaseCommand):
    help = "Populate analytics demo data: multiple Requests, Deals, Payments across dates and sources"

    def add_arguments(self, parser):
        parser.add_argument('--months', type=int, default=6, help='How many months back to generate')
        parser.add_argument('--per-month', type=int, default=5, help='Objects per month per model')

    def handle(self, *args, **opts):
        months = opts['months']
        per_month = opts['per_month']
        created = 0
        with transaction.atomic():
            created += self._gen_requests(months, per_month)
            created += self._gen_deals(months, per_month)
            created += self._gen_payments(months, per_month)
        self.stdout.write(self.style.SUCCESS(f'Analytics demo created ~{created} records'))

    def _rand_date(self, month_offset: int):
        now = timezone.now()
        base = (now - timedelta(days=30*month_offset)).replace(day=1, hour=12, minute=0, second=0, microsecond=0)
        delta_days = random.randint(0, 27)
        return base + timedelta(days=delta_days)

    def _pick(self, qs):
        lst = list(qs.order_by('?')[:1])
        return lst[0] if lst else None

    def _gen_requests(self, months, per_month):
        from crm.models import Request
        from crm.models.others import LeadSource
        from common.models import Department
        created = 0
        dept = Department.objects.order_by('id').first()
        sources = list(LeadSource.objects.all()[:5])
        for m in range(months):
            for i in range(per_month):
                dt = self._rand_date(m)
                ls = random.choice(sources) if sources else None
                Request.objects.create(
                    description=f'Demo request {m}-{i} (Generated for analytics)',
                    department=dept,
                    lead_source=ls,
                    receipt_date=dt.date(),
                    email=f'user{m}{i}@example.test',
                )
                created += 1
        return created

    def _gen_deals(self, months, per_month):
        from crm.models import Deal, Company, Contact
        from common.models import Department
        created = 0
        dept = Department.objects.order_by('id').first()
        comp = Company.objects.order_by('id').first()
        cont = Contact.objects.order_by('id').first()
        for m in range(months):
            for i in range(per_month):
                dt = self._rand_date(m)
                amount = random.randint(200, 5000)
                Deal.objects.create(
                    name=f'Demo deal {m}-{i}',
                    company=comp,
                    contact=cont,
                    amount=amount,
                    currency='USD',
                    department=dept,
                    created=dt,
                    updated=dt,
                )
                created += 1
        return created

    def _gen_payments(self, months, per_month):
        from crm.models import Payment, Company
        created = 0
        comp = Company.objects.order_by('id').first()
        for m in range(months):
            for i in range(per_month):
                dt = self._rand_date(m)
                amount = random.randint(100, 3000)
                Payment.objects.create(
                    company=comp,
                    amount=amount,
                    currency='USD',
                    payment_date=dt.date(),
                )
                created += 1
        return created
