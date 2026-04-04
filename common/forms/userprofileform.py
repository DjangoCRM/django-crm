from django import forms
from django.utils.translation import gettext as _

from common.models import UserProfile


class UserProfileForm(forms.ModelForm):
    is_active = forms.BooleanField(required=False)

    class Meta:
        model = UserProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = getattr(self, 'request', None).user
        if not user.is_superuser:
            del self.fields['is_active']

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if 'avatar' in self.changed_data and avatar:
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError(
                    _("Image file size exceeds 5MB limit"))
        return avatar
