from django import forms

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
