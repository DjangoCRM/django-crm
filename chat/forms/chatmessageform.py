from django import forms
from django.forms import ModelForm, Textarea
from django.utils.translation import gettext_lazy as _

from chat.models import ChatMessage


class ChatMessageForm(ModelForm):
    
    class Meta:
        model = ChatMessage
        fields = '__all__'
        widgets = {
            'content': Textarea(attrs={'cols': 80, 'rows': 3}),
            'content_type': forms.HiddenInput(),
            'object_id': forms.HiddenInput(),
            'answer_to': forms.HiddenInput(),
            'topic': forms.HiddenInput(),
            'owner': forms.HiddenInput(),
            'to': forms.HiddenInput(),
        }

    class Media:
        css = {"all": ("/static/common/css/hidden_field.css",)}       
        
    def clean_content(self):
        data = self.cleaned_data['content']
        if not data:
            raise forms.ValidationError(_("Please write a message"), code='invalid')
        return data     
    
    def clean_recipients(self):
        data = self.cleaned_data['recipients']
        if not data:
            raise forms.ValidationError(_("Please select at least one recipient"), code='invalid')
        return data 

    def save(self, commit=True):
        self.cleaned_data['to'] = self.cleaned_data['recipients']
        super().save(commit)
        return self.instance
