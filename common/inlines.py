from django import forms
from django.forms import ModelForm

from common.models import TheFile
from sharedkernel.inlines import BaseFileInline
from sharedkernel.inlines import register_file_inline
from sharedkernel.presentation import SAFE_ATTACH_FILE_ICON


class TheFileWidget(forms.ClearableFileInput):
    initial_text = ''
    template_name = 'common/widgets/clearable_file_input.html'


class InlineFileForm(ModelForm):
    class Meta:
        model = TheFile
        fields = ('file',)
        widgets = {'file': TheFileWidget}
        labels = {'file': ''}


class FileInline(BaseFileInline):
    form = InlineFileForm
    model = TheFile
    icon = SAFE_ATTACH_FILE_ICON


register_file_inline(FileInline)
