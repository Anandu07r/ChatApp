from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from chat.views import landing
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('chat/', include('chat.urls')),
    path('', landing, name='landing'),
    
    # Custom OTP Password Reset URLs
    path('password-reset/', user_views.password_reset_otp_view, name='password_reset'),
    path('password-reset/verify/', user_views.password_reset_verify_view, name='password_reset_verify'),
    path('password-reset/confirm/', user_views.password_reset_confirm_view, name='password_reset_confirm_otp'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    # Keep standard for backward compatibility or if needed, but primary flow is OTP
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
]
