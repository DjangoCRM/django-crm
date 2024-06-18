from django.contrib.contenttypes.models import ContentType
from crm.models import Company
from massmail.models import EmailAccount
from massmail.models import EmlAccountsQueue
from massmail.models import MassContact


def change_massconts(company: Company) -> None:
    """
    Changes or deletes a MassContact of a company and its contacts
    if their owners has changed.
    """
    email_account_id = None
    account_mc = MassContact.objects.filter(
        content_type=ContentType.objects.get_for_model(company),
        object_id=company.id
    )
    mcs = MassContact.objects.filter(
        content_type=ContentType.objects.get_for_model(company.contacts.model),
        object_id__in=company.contacts.all()
    )
    queue_obj = EmlAccountsQueue.objects.filter(owner=company.owner).first()
    if queue_obj:
        email_account_id = queue_obj.get_next()
        if email_account_id:
            email_account = EmailAccount.objects.get(id=email_account_id)
            account_mc.update(email_account=email_account)

        if mcs and email_account_id:
            for mc in mcs:
                email_account_id = queue_obj.get_next()
                email_account = EmailAccount.objects.get(id=email_account_id)            
                mc.email_account = email_account
                mc.save()
    if not queue_obj or not email_account_id:
        account_mc.delete()
        mcs.delete()
