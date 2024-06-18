from django.conf import settings
from django.contrib import messages
from django.forms import ModelForm
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

STR_FOR_TRANS = '\n{{% translate "{}" %}}'


def check_for_translation(request: HttpRequest, obj, form: ModelForm) -> None:
    if 'name' in form.changed_data:
        app_lable = obj._meta.app_label     # NOQA
        path = settings.BASE_DIR / app_lable / 'models' / 'to_translate.txt'
        try:
            f = open(path, 'r')
            txt = f.read()
            f.close()
        except FileNotFoundError:
            txt = ""
        if txt.find(obj.name) == -1:
            f = open(path, 'a+')
            f.write(STR_FOR_TRANS.format(obj.name))
            f.close()
            messages.info(request, _("The name has been added for translation."
                                     " Please update po and mo files."))
