from __future__ import annotations

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

class Command(BaseCommand):
    help = "Populate database with rich demo data across main models"

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No users found; run setupdata first.'))
            return
        created_total = 0
        with transaction.atomic():
            created_total += self._crm(user)
            created_total += self._tasks(user)
            created_total += self._chat(user)
            created_total += self._voip(user)
            created_total += self._integrations(user)
        self.stdout.write(self.style.SUCCESS(f'Demo data created/ensured, total created approx: {created_total}'))

    def _crm(self, user):
        from crm.models import Company, Contact, Lead, Deal, Request as CrmRequest, Product
        from crm.models import Payment
        from crm.models.others import LeadSource
        from common.models import Department
        created = 0
        dept = Department.objects.order_by('id').first()
        ls = LeadSource.objects.order_by('id').first()
        # Company
        comp, was = Company.objects.get_or_create(name='Acme Corp', defaults={'owner': user, 'department': dept})
        created += int(was)
        # Contact
        cont, was = Contact.objects.get_or_create(email='john.doe@acme.test', defaults={
            'first_name': 'John', 'last_name': 'Doe', 'owner': user, 'company': comp, 'department': dept,
        })
        created += int(was)
        # Lead
        lead, was = Lead.objects.get_or_create(email='lead@demo.test', defaults={
            'first_name': 'Alice', 'last_name': 'Demo', 'owner': user, 'lead_source': ls, 'department': dept,
        })
        created += int(was)
        # Product
        prod, was = Product.objects.get_or_create(name='Demo Product', defaults={'price': 199.0, 'owner': user})
        created += int(was)
        # Deal
        deal, was = Deal.objects.get_or_create(name='Acme First Deal', defaults={
            'company': comp, 'contact': cont, 'owner': user, 'amount': 1000, 'currency': 'USD', 'department': dept,
        })
        created += int(was)
        # Request
        req, was = CrmRequest.objects.get_or_create(subject='Need pricing', defaults={
            'owner': user, 'lead': lead, 'contact': cont, 'department': dept, 'message': 'Please send a quote',
        })
        created += int(was)
        # Payment (if model exists fields)
        try:
            pay, was = Payment.objects.get_or_create(company=comp, amount=500, defaults={'currency': 'USD'})
            created += int(was)
        except Exception:
            pass
        return created

    def _tasks(self, user):
        from tasks.models import Project, Task, Memo, Tag
        created = 0
        proj, was = Project.objects.get_or_create(name='Demo Project', defaults={'owner': user})
        created += int(was)
        tag, was = Tag.objects.get_or_create(name='demo')
        created += int(was)
        task, was = Task.objects.get_or_create(name='Call the client', defaults={'owner': user, 'project': proj})
        created += int(was)
        if was:
            task.tags.add(tag)
        memo, was = Memo.objects.get_or_create(subject='Kickoff notes', defaults={'owner': user, 'project': proj, 'content': 'Initial plan.'})
        created += int(was)
        return created

    def _chat(self, user):
        from chat.models import ChatMessage
        from crm.models import Request as CrmRequest
        created = 0
        req = CrmRequest.objects.order_by('-id').first()
        if req:
            cm, was = ChatMessage.objects.get_or_create(content_type=req.get_content_type(), object_id=req.id, content='Welcome to chat!', defaults={'owner': user})
            created += int(was)
        return created

    def _voip(self, user):
        created = 0
        try:
            from voip.models import IncomingCall
            ic, was = IncomingCall.objects.get_or_create(user=user, caller_id='+998901112233', defaults={'client_name': 'Acme Caller'})
            created += int(was)
        except Exception:
            pass
        return created

    def _integrations(self, user):
        from integrations.models import ChannelAccount, ExternalMessage
        created = 0
        ch = ChannelAccount.objects.filter(is_active=True).first()
        if ch:
            em, was = ExternalMessage.objects.get_or_create(channel=ch, direction='out', external_id='demo-1', defaults={'text': 'Demo message', 'sender_id': 'demo', 'recipient_id': 'client'})
            created += int(was)
        return created
