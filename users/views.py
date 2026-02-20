from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import CustomUser, PasswordResetCode
from .forms import (
    CustomUserCreationForm,
    OTPRequestForm,
    OTPVerifyForm,
    CustomSetPasswordForm,
    UserEditForm,
)



def register_view(request):
    if request.user.is_authenticated:
        return redirect("user_list")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully registered! Please log in.")
            return redirect("login")
    else:
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("user_list")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("user_list")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


def password_reset_otp_view(request):
    if request.method == "POST":
        form = OTPRequestForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            user = CustomUser.objects.filter(email=email).first()

            if user:
                # Generate code
                code = PasswordResetCode.generate_code()

                # Save code
                PasswordResetCode.objects.create(user=user, code=code)

                # Send email
                subject = "Your Password Reset Code"
                message = (
                    f"Hello {user.username},\n\n"
                    f"Your password reset code is: {code}\n\n"
                    f"This code is valid for 10 minutes."
                )

                send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

                # Store email in session
                request.session["reset_email"] = email

                messages.success(
                    request,
                    "A verification code has been sent to your email."
                )
                return redirect("password_reset_verify")

            else:
                messages.error(request, "No account found with this email.")

    else:
        form = OTPRequestForm()

    return render(
        request,
        "registration/password_reset_form.html",
        {"form": form}
    )


def password_reset_verify_view(request):
    email = request.session.get("reset_email")

    if not email:
        return redirect("password_reset")

    if request.method == "POST":
        form = OTPVerifyForm(request.POST)

        if form.is_valid():
            code = form.cleaned_data["code"]

            reset_code = (
                PasswordResetCode.objects.filter(
                    user__email=email,
                    code=code,
                    is_used=False,
                )
                .order_by("-created_at")
                .first()
            )

            if reset_code and reset_code.is_valid():
                reset_code.is_used = True
                reset_code.save()

                request.session["otp_verified"] = True
                return redirect("password_reset_confirm")

            else:
                messages.error(request, "Invalid or expired code.")

    else:
        form = OTPVerifyForm()

    return render(
        request,
        "registration/password_reset_verify.html",
        {
            "form": form,
            "email": email
        }
    )


def password_reset_confirm_view(request):
    email = request.session.get("reset_email")
    verified = request.session.get("otp_verified")

    if not email or not verified:
        return redirect("password_reset")

    user = CustomUser.objects.get(email=email)

    if request.method == "POST":
        form = CustomSetPasswordForm(user, request.POST)

        if form.is_valid():
            form.save()

            # Clear session
            del request.session["reset_email"]
            del request.session["otp_verified"]

            messages.success(
                request,
                "Your password has been reset successfully. You can now log in."
            )
            return redirect("login")

    else:
        form = CustomSetPasswordForm(user)

    return render(
        request,
        "registration/password_reset_confirm.html",
        {"form": form}
    )



@login_required
def profile_view(request):
    return render(request, "users/profile.html", {"user": request.user})

@login_required
def edit_profile_view(request):

    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your profile has been updated successfully!"
            )
            return redirect("profile")

    else:
        form = UserEditForm(instance=request.user)

    return render(
        request,
        "users/edit_profile.html",
        {"form": form}
    )