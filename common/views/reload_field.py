from typing import Union
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseForbidden

from common.utils.helpers import get_active_users
from common.utils.helpers import get_department_id
from massmail.views.signature_previews import signature_preview


def reload_field(request: WSGIRequest) -> Union[HttpResponse, HttpResponseForbidden, JsonResponse]:
    """Handle Ajax requests for update next form fields:
    'signature_preview', 'owner' and 'co_owner'"""
    
    #if request.headers.get('x-requested-with') != 'XMLHttpRequest':
    #    return HttpResponseForbidden()
        
    if 'signature' in request.GET:
        return signature_preview(request)
    
    department_id = request.GET.get('department')
    if department_id:
        q_params = Q(groups__name__in=('managers', 'operators', 'superoperators'))
        active_users = get_active_users()
        if request.user.is_superuser or request.user.is_superoperator:  # NOQA
            q_params |= Q(is_superuser=True)
        else:
            department_id = get_department_id(
                request.user
            ) or request.session.get('department_id') or department_id

        users = active_users.filter(q_params).filter(groups=department_id)
        dynamic_choices = [
            {'label': u[1], 'value': str(u[0])}
            for u in users.distinct().values_list('id', 'username')
        ]
        dynamic_choices.insert(0,  {'label': '---------', 'value': ''})
        return JsonResponse({'choices': dynamic_choices})
    return JsonResponse({'choices': [{'label': '---------', 'value': ''}]})
