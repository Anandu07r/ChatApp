from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.core.exceptions import ValidationError
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Email already registered.")

        return email



class OTPRequestForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control-custom",
            "placeholder": "your@email.com"
        })
    )

class OTPVerifyForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        label="Verification Code",
        widget=forms.TextInput(attrs={
            "class": "form-control-custom",
            "placeholder": "6-digit code",
            "style": "text-align:center;letter-spacing:12px;font-size:24px;"
        })
    )

    def clean_code(self):
        code = self.cleaned_data["code"]

        if not code.isdigit():
            raise ValidationError("Code must be numeric.")

        return code



class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control-custom",
                "placeholder": "Min. 8 characters"
            })


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control-custom"

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError("This email is already in use.")

        return email