from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .models import CustomUser, PasswordResetCode
from .forms import (
    CustomUserCreationForm,
    EmailLoginForm,       
    OTPRequestForm,
    OTPVerifyForm,
    CustomSetPasswordForm,
    UserEditForm,
)



def register_view(request):
    if request.user.is_authenticated:
        return redirect("user_list")

    form = CustomUserCreationForm(request.POST or None)

    if form.is_valid():
        form.save()
        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "register.html", {"form": form})



def login_view(request):
    if request.user.is_authenticated:
        return redirect("user_list")

    form = EmailLoginForm(request, data=request.POST or None)

    if form.is_valid():
        user = form.get_user()

        # mark online
        user.is_online = True
        user.save(update_fields=["is_online"])

        login(request, user)
        return redirect("user_list")

    return render(request, "login.html", {"form": form})


def logout_view(request):
    if request.user.is_authenticated:
        request.user.is_online = False
        request.user.save(update_fields=["is_online"])

    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


def password_reset_otp_view(request):
    form = OTPRequestForm(request.POST or None)

    if form.is_valid():
        email = form.cleaned_data["email"].lower()

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.error(request, "No account found with that email.")
            return redirect("password_reset")

        code = PasswordResetCode.generate_code()

        PasswordResetCode.objects.create(
            user=user,
            code=code
        )

        send_mail(
            subject="Password Reset Code",
            message=f"Your password reset code is {code}. It expires in 10 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        request.session["reset_email"] = email
        messages.success(request, "Verification code sent to your email.")
        return redirect("password_reset_verify")

    return render(request, "registration/password_reset_form.html", {"form": form})



def password_reset_verify_view(request):
    email = request.session.get("reset_email")

    if not email:
        return redirect("password_reset")

    form = OTPVerifyForm(request.POST or None)

    if form.is_valid():
        code = form.cleaned_data["code"]

        record = (
            PasswordResetCode.objects
            .filter(user__email=email, code=code, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if record and record.is_valid():
            record.is_used = True
            record.save(update_fields=["is_used"])

            request.session["otp_verified"] = True
            return redirect("password_reset_confirm")

        messages.error(request, "Invalid or expired code.")

    return render(
        request,
        "registration/password_reset_verify.html",
        {"form": form, "email": email},
    )


def password_reset_confirm_view(request):
    email = request.session.get("reset_email")
    verified = request.session.get("otp_verified")

    if not email or not verified:
        return redirect("password_reset")

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return redirect("password_reset")

    form = CustomSetPasswordForm(user, request.POST or None)

    if form.is_valid():
        form.save()

        request.session.pop("reset_email", None)
        request.session.pop("otp_verified", None)

        messages.success(request, "Password reset successful. You can now log in.")
        return redirect("login")

    return render(
        request,
        "registration/password_reset_confirm.html",
        {"form": form},
    )



@login_required
def profile_view(request):
    return render(request, "users/profile.html", {"user": request.user})


@login_required
def edit_profile_view(request):
    form = UserEditForm(request.POST or None, instance=request.user)

    if form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")

    return render(request, "users/edit_profile.html", {"form": form})