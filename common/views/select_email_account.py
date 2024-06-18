from django import forms
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from crm.models import Request
from crm.site.crmadminsite import crm_site
from massmail.models import EmailAccount


class EaForm(forms.Form):
    
    def __init__(self, ea_choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ea'].choices = ea_choices
        self.fields['ea'].initial = ea_choices[0]
        
    ea = forms.ChoiceField(label='', choices=(), widget=forms.RadioSelect)


def select_email_account(request: WSGIRequest):
    if request.method == "POST":
        ea_id = request.POST.get('ea')
        url = reverse('select_emails_import_request') + f"?ea={ea_id}"
        params = request.GET.copy()
        del params['eas']
        return HttpResponseRedirect(url + f'&{params.urlencode()}')
        
    else:
        ids_str = request.GET.get('eas')
        ids = ids_str.split(',')
        eas = EmailAccount.objects.filter(
            id__in=ids
        ).distinct().order_by('name').values_list('id', 'name')
        form = EaForm(eas)
        extra_context = dict(
            crm_site.each_context(request),
            opts=Request._meta,     # NOQA
            form=form
        )            
            
    return render(request, 'common/select_email_account.html', extra_context)
