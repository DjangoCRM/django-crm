from django import forms


class ConnectionForm(forms.Form):
    callerid = forms.ChoiceField(label='Caller ID')
    to_number = forms.CharField(widget=forms.HiddenInput)
    
