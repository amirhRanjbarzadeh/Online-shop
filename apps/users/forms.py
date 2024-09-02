from django import forms


class EmailForm(forms.Form):
    email = forms.EmailField()


class CodeVerificationForm(forms.Form):
    email = forms.EmailField()
    code = forms.CharField(max_length=8)


class SignUpForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)