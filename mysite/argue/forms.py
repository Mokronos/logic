from django import forms

class UserForm(forms.Form):
    username = forms.CharField(label="Username", max_length=64)
    email = forms.CharField(label="Email", max_length=64)
