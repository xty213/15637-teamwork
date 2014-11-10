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


class PostItemForm(forms.Form):
    name = forms.CharField(max_length=128)
    category = forms.IntegerField()
    mode = forms.CharField(max_length=10)
    price = forms.FloatField()
    endtime = forms.DateTimeField(required=False)
    description = forms.CharField(max_length=1024, required=False)

    def clean(self):
        cleaned_data = super(PostItemForm, self).clean()

        if not 1 <= cleaned_data.get('category') <= 15:
            raise forms.ValidationError('Invalid category.')

        if not cleaned_data.get('mode') in ['fixed', 'auction']:
            raise forms.ValidationError('Invalid price mode.')

        if cleaned_data.get('mode') == 'auction' and not cleaned_data.get('endtime'):
            raise forms.ValidationError('Auction mode must be associated with end time.')

        return cleaned_data