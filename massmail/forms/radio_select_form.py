from django import forms


class RadioSelectForm(forms.Form):

    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['choice'].choices = choices
        self.fields['choice'].initial = choices[0]

    choice = forms.ChoiceField(label='', choices=(), widget=forms.RadioSelect)
