from email.utils import parseaddr
from django.apps import apps
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from common.models import Base1
from common.utils.helpers import add_phone_q_params
from common.utils.helpers import get_department_id
from crm.utils.helpers import get_email_domain
from crm.utils.ticketproc import new_ticket


class Request(Base1):
    class Meta:
        verbose_name = _("Request")
        verbose_name_plural = _("Requests")

    request_for = models.CharField(
        max_length=250, null=False, blank=False,
        verbose_name=_("Request for"),
    )
    first_name = models.CharField(
        max_length=100, null=False, blank=False,
        verbose_name=_("First name"),
        help_text=_("The name of the contact person (one word).")
    )
    middle_name = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name=_("Middle name"),
        help_text=_("The middle name of the contact person.")
    )
    last_name = models.CharField(
        max_length=100, blank=True, default='',
        verbose_name=_("Last name"),
        help_text=_("The last name of the contact person (one word).")
    )
    email = models.CharField(max_length=250, blank=True, default='')

    phone = models.CharField(max_length=200, blank=True, default='')

    website = models.URLField(max_length=200, blank=True, default='')

    lead_source = models.ForeignKey(
        'LeadSource', blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Lead source"),
        help_text=_("Lead Source")
    )
    company_name = models.CharField(
        max_length=200, blank=True, default='',
        verbose_name=_("Company name"),
    )
    receipt_date = models.DateField(
        blank=True, null=True,
        verbose_name=_("Date of receipt"),
        help_text=_("Date of receipt of the request.")
    )
    lead = models.ForeignKey(
        'Lead', blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name=_("Lead")
    )
    contact = models.ForeignKey(
        'Contact', blank=True, null=True, on_delete=models.CASCADE,
        verbose_name=_("Contact")
    )
    company = models.ForeignKey(
        'Company', blank=True, null=True, on_delete=models.CASCADE,
        related_name="requests",
        verbose_name=_("Company of contact")
    )
    deal = models.ForeignKey(
        'Deal', blank=True, null=True, on_delete=models.CASCADE,
        verbose_name=_("Deal"),
        related_name="requests",
    )
    products = models.ManyToManyField(
        'Product', blank=True,
        verbose_name=_("Products")
    )
    country = models.ForeignKey(
        'Country', blank=True, null=True,
        verbose_name=_("Country"),
        on_delete=models.SET_NULL
    )
    city = models.ForeignKey(
        'City', blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("City"),
        help_text=_("Object of City in database")
    )
    city_name = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name=_("City")
    )
    description = models.TextField(
        blank=True, default='',
        verbose_name=_("Description"),
    )
    translation = models.TextField(
        blank=True, default='',
        verbose_name=_("Translation"),
    )
    remark = models.TextField(
        blank=True, default='',
        verbose_name=_("Remark"),
    )
    pending = models.BooleanField(
        default=True,
        verbose_name=_("Pending"),
        help_text=_("Waiting for validation of fields filling")
    )
    subsequent = models.BooleanField(
        default=False,
        verbose_name=_("Subsequent"),
        help_text=_(
            "Received from the client with whom you are already cooperate")
    )
    duplicate = models.BooleanField(
        default=False,
        verbose_name=_("Duplicate"),
        help_text=_("Duplicate request. The deal will not be created.")
    )
    verification_required = models.BooleanField(
        default=False,
        verbose_name=_("Verification required"),
        help_text=_("Links are set automatically and require verification.")
    )
    ticket = models.CharField(
        max_length=16, default=new_ticket
    )
    co_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name=_("Co-owner"),
        related_name="%(app_label)s_%(class)s_co_owner_related",
    )
    files = GenericRelation('common.TheFile')

    def clean(self):
        if self.contact and self.company:
            if self.contact.company != self.company:
                raise ValidationError({
                    'contact': _("Company and contact person do not match."),
                    'company': _("Company and contact person do not match.")
                })
        if self.contact and self.lead:
            raise ValidationError({
                'contact': _("Specify the contact person or lead. But not both."),
                'company': _("Specify the contact person or lead. But not both.")
            })

    def __str__(self):
        return self.request_for

    def get_absolute_url(self):
        return reverse('site:crm_request_change', args=(self.id,))

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    def find_contact_or_lead(self) -> bool:
        phone_params = email_params = models.Q()
        contacts1 = contacts2 = contacts3 = None
        if self.phone:
            phone_params = add_phone_q_params(self.phone)
        if self.email:
            _, email = parseaddr(self.email)
            email_params = models.Q(email__icontains=email)
            email_params |= models.Q(secondary_email__icontains=email)
        contact_model = apps.get_model('crm', 'Contact')
        lead_model = apps.get_model('crm', 'Lead')
        for model, attr in ((contact_model, 'contact'), (lead_model, 'lead')):
            args = []
            contacts1_len = contacts2_len = contacts3_len = 0
            kwargs = {"first_name__iexact": self.first_name}
            if email_params:
                args.append(email_params)
                contacts1 = model.objects.filter(*args, **kwargs)
                contacts1_len = contacts1.count()
                if contacts1_len == 1:
                    self._set_contact(attr, contacts1)
                    return True

            if phone_params:
                if contacts1_len > 1:
                    args.append(phone_params)
                else:
                    args = [email_params | phone_params]
                contacts2 = model.objects.filter(*args, **kwargs)
                contacts2_len = contacts2.count()
                if contacts2_len == 1:
                    self._set_contact(attr, contacts2)
                    return True

            if self.last_name:
                kwargs["last_name__iexact"] = self.last_name
                if contacts2_len > 1:
                    contacts3 = model.objects.filter(*args, **kwargs)
                    contacts3_len = contacts3.count()
                    if contacts3_len == 0 and not any((contacts2, contacts1)):
                        continue
                    if len(contacts3) == 1:
                        self._set_contact(attr, contacts3)
                        return True

            if self.company_name and any((contacts3, contacts2, contacts1)) or self.last_name:

                if model == contact_model:
                    company_params = models.Q(company__full_name__icontains=self.company_name)
                    company_params |= models.Q(company__full_name__in=self.company_name)
                else:
                    company_params = models.Q(company_name__icontains=self.company_name)
                    company_params |= models.Q(company_name__in=self.company_name)

                if contacts3_len > 1:
                    contacts4 = contacts3.filter(company_params)
                else:
                    contacts4 = model.objects.filter(company_params, **kwargs)

                if len(contacts4) == 0 and not any((contacts3, contacts2, contacts1)):
                    continue
                if len(contacts4) >= 1:
                    self._set_contact(attr, contacts4)
                    return True

            if any((contacts3, contacts2, contacts1)):
                for contacts in (contacts3, contacts2, contacts1):
                    if contacts:
                        self._set_contact(attr, contacts)
                        return True
        return False

    def _set_contact(self, attr: str, contacts: models.query.QuerySet) -> None:
        contact = contacts.first()
        if attr == 'contact':
            if self.company:
                if self.company == contact.company:
                    self.contact = contact
            else:
                self.contact = contact
                self.company = contact.company
        else:
            self.lead = contact
        self.verification_required = True

    def parseweb(self) -> str:
        """Parse the website address..

        Returns:
            str: the website domain.
        """
        website = self.website
        try:
            website = website.split("www.")[1]
        except IndexError:
            try:
                website = website.split("//")[1]
            except IndexError:
                pass
        return website.split("/")[0]

    def find_company(self) -> None:
        if not all((self.company, self.contact, self.lead)):
            companies4 = companies3 = companies2 = companies1 = None
            companies1_len = companies2_len = companies3_len = companies4_len = 0
            company_model = apps.get_model('crm', 'Company')
            contact_model = apps.get_model('crm', 'Contact')
            if self.email:
                realname, email = parseaddr(self.email)  # NOQA
                contact_email_param = models.Q(email__icontains=email)
                contact_email_param |= models.Q(secondary_email__icontains=email)
                companies1 = contact_model.objects.filter(
                    contact_email_param
                ).values_list('company_id', flat=True)
                companies1_len = companies1.count()
                if companies1_len == 1:
                    self.company_id = companies1.first()
                    if self.company_id:
                        self.verification_required = True
                    return

            if self.phone:
                contact_phone_param = add_phone_q_params(self.phone)
                if companies1_len > 1:
                    companies2 = contact_model.objects.filter(
                        contact_phone_param, company_id__in=companies1
                    ).values_list('company_id', flat=True)
                else:
                    companies2 = contact_model.objects.filter(
                        contact_phone_param
                    ).values_list('company_id', flat=True)
                companies2_len = companies2.count()
                if companies2_len == 1:
                    self.company_id = companies2.first()
                    if self.company_id:
                        self.verification_required = True
                    return

            if self.company_name:
                name_param = self._get_company_name_q_param()
                if companies1_len > 1:
                    companies3 = company_model.objects.filter(name_param, id__in=companies1)
                elif companies2_len > 1:
                    companies3 = company_model.objects.filter(name_param, id__in=companies2)
                else:
                    companies3 = company_model.objects.filter(name_param)
                companies3_len = companies3.count()
                if companies3_len == 1:
                    self.company = companies3.first()
                    if self.company:
                        self.verification_required = True
                    return

                if self.country:
                    if companies3_len > 1:
                        companies4 = companies3.filter(country=self.country)
                    elif companies1_len > 1:
                        companies4 = company_model.objects.filter(country=self.country, id__in=companies1)
                    elif companies2_len > 1:
                        companies4 = company_model.objects.filter(country=self.country, id__in=companies2)
                    if companies4 is not None:
                        companies4_len = companies4.count()
                        if companies4_len == 1:
                            self.company = companies4.first()
                            if self.company:
                                self.verification_required = True
                            return

                    if self.website and companies4_len > 1:
                        website = self.parseweb()
                        companies5 = companies4.filter(website__icontains=website)
                        companies5_len = companies5.count()
                        if companies5_len >= 1:
                            self.company = companies5.first()
                            if self.company:
                                self.verification_required = True
                            return

            if not any((companies4_len, companies3_len, companies2_len, companies1_len)):
                if self.email:
                    email_domain = get_email_domain(self.email)
                    if email_domain:
                        self.company = company_model.objects.filter(
                            email__icontains=f"@{email_domain}"
                        ).first()
                        if self.company:
                            self.verification_required = True
            else:
                for companies in (companies4, companies3, companies2):
                    if companies:
                        value = companies.first()
                        if type(value) is int:
                            self.company_id = value
                        else:
                            self.company = value
                        if self.company:
                            self.verification_required = True

    def _get_company_name_q_param(self) -> models.Q:
        letters = [i for i in self.company_name if i.isalpha() or i.isspace()]
        phrase = ''.join(letters)
        words = phrase.split(" ")
        words_re_list = [''.join((f"[{letter}]{{1}}" for letter in word)) for word in words]
        phrase_re = ''.join((f'[^a-zA-z]*{word_re}' for word_re in words_re_list))
        return models.Q(full_name__iregex=fr"^{phrase_re}[^a-zA-z]*$")

    def get_or_create_contact_or_lead(self) -> None:
        if self.find_contact_or_lead():
            self.verification_required = True
            return
        self.find_company()
        if all((self.company, self.first_name, self.email)):
            contact_model = apps.get_model('crm', 'Contact')
            contact = contact_model.objects.create(
                first_name=self.first_name,
                last_name=self.last_name,
                email=self.email,
                country=self.company.country,
                company=self.company,
                department_id=get_department_id(self.company.owner),
                owner=self.company.owner,
            )
            self.contact = contact
            self.verification_required = True
            return

        lead_model = apps.get_model('crm', 'Lead')
        lead = lead_model(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            phone=self.phone,
            company_name=self.company_name,
            lead_source=self.lead_source,
            country=self.country,
            city_name=self.city_name,
            city=self.city,
            department_id=get_department_id(self.owner),
            owner=self.owner,
        )
        if self.company:
            lead.company = self.company
            lead.company_name = self.company.full_name
            lead.website = self.company.website
            lead.company_email = self.company.email
            lead.type = self.company.type
        lead.save()
        if self.company:
            lead.industry.set(self.company.industry.all())
        self.lead = lead
        self.company = None
        self.verification_required = True

    def update_request_data(self) -> None:
        if self.contact:
            self.phone = self.contact.phone
            self.company_name = self.contact.company.full_name
            self.company = self.contact.company
            self.country = self.contact.company.country
            self.city = self.contact.company.city
            self.website = self.contact.company.website
            self.owner = self.contact.owner
        elif self.lead:
            self.owner = self.lead.owner
            if not self.phone and self.lead.phone:
                self.phone = self.lead.phone
