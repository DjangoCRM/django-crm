import hmac
import requests
from hashlib import sha1
from base64 import b64decode
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpRequest
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from typing import Optional
from typing import Tuple

from common.utils.helpers import add_phone_q_params
from crm.models import Contact
from crm.models import Deal
from crm.models import Lead


@method_decorator(csrf_exempt, name='dispatch')
class VoIPWebHook(View):
    """WebHook for Zadarma VoIP provider"""

    @staticmethod
    def get(request):
        return HttpResponse(request.GET.get('zd_echo'), '')

    @staticmethod
    def post(request):
        phone: str = ''
        entry: str = ''
        data: str = ''
        e: str = ''
        init_str = full_name = deal = ''
        event = request.POST.get('event')
        if event == 'NOTIFY_RECORD':
            return HttpResponse('')
        # call status
        answered = request.POST.get('disposition') == 'answered'
        # the end of an outgoing call from the PBX
        if event == 'NOTIFY_OUT_END':
            # the phone number that was called
            init_str = _('An outgoing call to')
            phone = request.POST.get('destination')
            internal = request.POST.get('internal')
            call_start = request.POST.get('call_start')
            data = internal + phone + call_start
            
        # the end of an incoming call to the PBX extension number    
        elif event == 'NOTIFY_END':
            # the caller's phone number
            init_str = _('An incoming call from')
            phone = request.POST.get('caller_id')
            called_did = request.POST.get('called_did')
            call_start = request.POST.get('call_start')
            data = phone + called_did + call_start            
            
        if is_authenticated(request, data):
            duration = round(int(request.POST.get('duration'))/60, 1)
            # if phone:
            contact, lead, deal, e = find_objects_by_phone(phone)
            if not e:
                obj = contact or lead
                if obj:
                    obj.was_in_touch_today()
                    full_name = obj.full_name
        
                if deal:
                    duration_str = _(f'(duration: {duration} minutes)')
                    entry = f'{init_str} {full_name} {duration_str}.'
                    deal.add_to_workflow(entry)
                    deal.save()
                    
                if not any((contact, lead, deal)) and settings.VOIP_FORWARD_DATA:
                    url = settings.VOIP_FORWARD_URL
                    headers = {'Signature': request.headers['Signature']}
                    requests.post(url, data=request.POST, headers=headers)

        return HttpResponse('')
    

def is_authenticated(request: HttpRequest, data: str) -> bool:
    """Authenticate request"""
    if not data:
        return False
    signature = request.headers.get('Signature')
    backend = next(
        b for b in settings.VOIP 
        if b['PROVIDER'] == 'Zadarma'
    )
    ip = request.META['REMOTE_ADDR']
    if ip != backend['IP']:
        if ip != settings.VOIP_FORWARDING_IP:
            return False
    secret = backend['OPTIONS']['secret']
    hmac_h = hmac.new(
        secret.encode(), 
        data.encode(), 
        sha1
    )     
    bts = bytes(hmac_h.hexdigest(), 'utf8')
    return True if b64decode(signature) == bts else False


def find_objects_by_phone(phone: str) -> \
        Tuple[Optional[Contact], Optional[Lead], Optional[Deal], str]:
    """Search Contact, Lead and active Deal by phone number"""
    params = contact = lead = deal = None
    q_params = add_phone_q_params(phone)
    try:
        contact = Contact.objects.filter(q_params).first()
    except Exception as e:
        return contact, lead, deal, str(e)
    if contact:
        params = {'contact_id': contact.id, 'active': True}
    else:
        lead = Lead.objects.filter(q_params).first()
        if lead:
            params = {'lead_id': lead.id, 'active': True}
    if any((contact, lead)):
        deal = Deal.objects.filter(**params).order_by('-update_date').first()

    return contact, lead, deal, ''
