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


class ResetPasswordForm(forms.Form):
    password = forms.CharField()
    password2 = forms.CharField()

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()

        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if not password == password2:
            raise forms.ValidationError('Passwords did not match.')

        return cleaned_data


class PostItemForm(forms.Form):
    name = forms.CharField(max_length=128)
    category = forms.IntegerField(required=True)
    mode = forms.CharField(max_length=10)
    price = forms.FloatField()
    endtime = forms.DateTimeField(required=False, input_formats=["%Y/%m/%d %H:%M"])
    description = forms.CharField(max_length=1024, required=False)
    pic1 = forms.ImageField(required=False)
    pic2 = forms.ImageField(required=False)
    pic3 = forms.ImageField(required=False)
    pic4 = forms.ImageField(required=False)

    def clean(self):
        cleaned_data = super(PostItemForm, self).clean()

        if not 1 <= cleaned_data.get('category') <= 15:
            raise forms.ValidationError('Invalid category.')

        if not cleaned_data.get('mode') in ['fixed', 'auction']:
            raise forms.ValidationError('Invalid price mode.')

        if cleaned_data.get('mode') == 'auction' and not cleaned_data.get('endtime'):
            raise forms.ValidationError('Auction mode must be associated with end time.')

        return cleaned_data


class PostDemandForm(forms.Form):
    name = forms.CharField(max_length=128)
    category = forms.IntegerField(required=True)
    price = forms.FloatField()
    description = forms.CharField(max_length=1024, required=False)
