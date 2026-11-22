from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from common.utils.helpers import OBJ_DOESNT_EXIT_STR


def object_not_found_response(request, model_admin, object_id):
    messages.error(
        request,
        OBJ_DOESNT_EXIT_STR.format(
            model_admin.model._meta.verbose_name,
            object_id
        )
    )
    return HttpResponseRedirect(
        reverse(
            f"site:{model_admin.opts.app_label}_"
            f"{model_admin.model.__name__.lower()}_changelist"
        )
    )
