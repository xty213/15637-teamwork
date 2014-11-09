from django import forms
from models import *

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField()
    password2 = forms.CharField()

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()

        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if not password == password2:
            raise forms.ValidationError('Passwords did not match.')

        return cleaned_data

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(User.objects.filter(username=username)) > 0:
            raise forms.ValidationError('This AndrewID has registered an account.')

        return username
