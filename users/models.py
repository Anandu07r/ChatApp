from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import datetime
import random


class CustomUser(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class PasswordResetCode(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="reset_codes"
    )
    code = models.CharField(max_length=6, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def is_valid(self):
        expiry = self.created_at + datetime.timedelta(minutes=10)
        return not self.is_used and timezone.now() < expiry

    @staticmethod
    def generate_code():
        return str(random.SystemRandom().randint(100000, 999999))

    def __str__(self):
        return f"{self.user.email} - {self.code}"