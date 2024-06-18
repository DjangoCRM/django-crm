from django import forms
import os


class AddFilesForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fl = args[0]
        for f in fl:
            field_name = f.path.split(os.sep)[-1]
            self.fields[field_name] = forms.BooleanField(
                required=False, initial=False
            )
