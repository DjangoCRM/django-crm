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
            created_total += self._users()
            created_total += self._crm(user)
            created_total += self._tasks(user)
            created_total += self._chat(user)
            created_total += self._voip(user)
            created_total += self._integrations(user)
        self.stdout.write(self.style.SUCCESS(f'Demo data created/ensured, total created approx: {created_total}'))

    def _users(self):
        from django.contrib.auth.models import Group
        from common.models import Department
        User = get_user_model()
        created = 0
        dept_global = Department.objects.filter(name__icontains='Global').first() or Department.objects.first()
        dept_local = Department.objects.exclude(pk=getattr(dept_global, 'pk', None)).first() or dept_global
        mgr_group, _ = Group.objects.get_or_create(name='managers')
        # Manager 1 (Global)
        u1, was = User.objects.get_or_create(username='manager1', defaults={'email': 'manager1@example.com', 'is_active': True})
        if was:
            u1.set_password('demo1234'); u1.save(); created += 1
        u1.groups.add(mgr_group, dept_global)
        # Manager 2 (Local)
        u2, was = User.objects.get_or_create(username='manager2', defaults={'email': 'manager2@example.com', 'is_active': True})
        if was:
            u2.set_password('demo1234'); u2.save(); created += 1
        u2.groups.add(mgr_group, dept_local)
        return created

    def _crm(self, user):
        from crm.models import Company, Contact, Lead, Deal, Request as CrmRequest, Product
        from crm.models import Payment
        from crm.models.others import LeadSource
        from common.models import Department
        created = 0
        dept = Department.objects.order_by('id').first()
        ls = LeadSource.objects.order_by('id').first()
        # Company
        comp, was = Company.objects.get_or_create(full_name='Acme Corp', defaults={'owner': user, 'department': dept})
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
        from decimal import Decimal
        prod, was = Product.objects.get_or_create(name='Demo Product', defaults={'price': Decimal('199.00'), 'type': 'G'})
        created += int(was)
        # Deal
        from django.utils import timezone
        deal, was = Deal.objects.get_or_create(name='Acme First Deal', defaults={
            'company': comp,
            'contact': cont,
            'owner': user,
            'amount': 1000,
            'currency': None,  # FK
            'department': dept,
            'next_step': 'Initial contact',
            'next_step_date': timezone.now().date(),
        })
        created += int(was)
        # Request
        req, was = CrmRequest.objects.get_or_create(description='Need pricing', defaults={
            'owner': user,
            'lead': lead,
            'contact': cont,
            'department': dept,
            'company_name': 'Acme Corp',
            'email': 'buyer@acme.test',
            'phone': '+998901234567',
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
        from django.contrib.contenttypes.models import ContentType
        from crm.models import Request as CrmRequest
        created = 0
        reqs = list(CrmRequest.objects.order_by('-id')[:2])
        for idx, req in enumerate(reqs, start=1):
            ct = ContentType.objects.get_for_model(req)
            msgs = [
                f'Welcome to chat! (thread {idx})',
                'Client: Hello, I need details about your product.',
                'Manager: Sure, sending spec sheet now.',
            ]
            for m in msgs:
                cm, was = ChatMessage.objects.get_or_create(content_type=ct, object_id=req.id, content=m, defaults={'owner': user})
                created += int(was)
        return created

    def _voip(self, user):
        created = 0
        try:
            from voip.models import IncomingCall
            from crm.models.others import CallLog
            # Incoming calls for two demo numbers
            numbers = ['+998901112233', '+998909998877']
            for n in numbers:
                ic, was = IncomingCall.objects.get_or_create(user=user, caller_id=n, defaults={'client_name': 'Demo Caller'})
                created += int(was)
                cl, was = CallLog.objects.get_or_create(user=user, number=n, direction='inbound', defaults={'duration': 60})
                created += int(was)
        except Exception:
            pass
        return created

    def _integrations(self, user):
        from integrations.models import ChannelAccount, ExternalMessage
        created = 0
        chs = list(ChannelAccount.objects.filter(is_active=True)[:2])
        for i, ch in enumerate(chs, start=1):
            em, was = ExternalMessage.objects.get_or_create(
                channel=ch, direction='out', external_id=f'demo-{i}',
                defaults={'text': f'Demo message {i}', 'sender_id': 'demo', 'recipient_id': 'client'}
            )
            created += int(was)
        return created
