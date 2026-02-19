from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')

class OTPRequestForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control-custom', 'placeholder': 'your@email.com'}))

class OTPVerifyForm(forms.Form):
    code = forms.CharField(max_length=6, label="Verification Code", widget=forms.TextInput(attrs={'class': 'form-control-custom', 'placeholder': '6-digit code', 'style': 'text-align: center; letter-spacing: 12px; font-size: 24px;'}))

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control-custom'
            field.widget.attrs['placeholder'] = 'Min. 8 characters'

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control-custom'
