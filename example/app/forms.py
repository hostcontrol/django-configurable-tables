from django import forms


class LoginForm(forms.Form):

    username = forms.CharField(help_text="Username: test")
    password = forms.CharField(help_text="Password: test", widget=forms.PasswordInput)
