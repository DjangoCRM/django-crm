from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext
from django.utils.safestring import mark_safe
from django.conf import settings
from django.urls import reverse
from django.utils import translation

# from django.utils.text import slugify


WORK_WITH_CHOICES = (
    ('l', _('list')),
    ('i', _('instance'))
)


def get_language_code_choices():
    return settings.LANGUAGES


class Page(models.Model):
    class Meta:
        verbose_name = _("Help page")
        verbose_name_plural = _("Help pages")

    app_label = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name=_("app label"),
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name=_("model"),
    )
    page = models.CharField(
        max_length=1,
        blank=True,
        default='',
        choices=WORK_WITH_CHOICES,
        verbose_name=_("page"),
    )
    title = models.CharField(
        max_length=250, null=True, blank=True,
        # help_text=_("Title"),
        verbose_name=_("Title"),
    )
    main = models.BooleanField(
        default=False,
        verbose_name=_("Available on CRM page"),
        help_text=_(
            "Available on one of CRM pages. Otherwise, it can only be accessed via a link from another help page."),
    )
    language_code = models.CharField(
        max_length=7,
        default='',
        blank=True,
        choices=get_language_code_choices(),
        verbose_name=_("Language"),
    )

    def __str__(self):
        return gettext(self.model)

    def get_absolute_url(self):
        return reverse("admin:help_page_change", args=(self.id,))

    def get_url(self, user) -> str:
        """Returns help page url if paragraphs exist for current User & language."""
        q_params = models.Q(language_code=translation.get_language())
        q_params &= models.Q(draft=False)
        if not user.is_superuser:
            user_groups = user.groups.all()
            q_params &= models.Q(groups__in=user_groups)
        if self.paragraph_set.filter(q_params).exists():
            url = reverse('site:help_page_change', args=(self.id,))
            return url
        return ''


class Paragraph(models.Model):
    class Meta:
        verbose_name = _("Paragraph")
        verbose_name_plural = _("Paragraphs")
        ordering = ["index_number"]

    document = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
    )
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        verbose_name=_("Groups"),
        help_text=_(
            "If no user group is selected then the paragraph "
            "will be available only to the superuser."
            )
    )
    title = models.CharField(
        max_length=250, null=True, blank=True,
        help_text=_("Title of paragraph."),
        verbose_name=_("Title"),
    )
    content = models.TextField(
        blank=True, default=''
    )
    language_code = models.CharField(
        max_length=7,
        # default='',
        # blank=True,
        choices=get_language_code_choices(),
        verbose_name=_("Language"),
    )
    draft = models.BooleanField(
        default=True,
        verbose_name=_("draft"),
        help_text=_("Will not be published."),
    )
    verification_required = models.BooleanField(
        default=True,
        verbose_name=_("Verification required"),
        help_text=_("Content requires additional verification."),
    )
    index_number = models.SmallIntegerField(
        null=False, blank=False,
        default=1,
        verbose_name=_("Index number"),
        help_text=_("The sequence number of the paragraph on the page.")
    )
    link1 = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text=_("Link to a related paragraph if exists.")
    )

    def __str__(self):
        if self.title:
            return mark_safe(f'<a id="paragraph-{self.id}">{self.title}</a>')
        return f'{self.id}'
