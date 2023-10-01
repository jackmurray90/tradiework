from django.db import models
from django.contrib.auth.models import User
import re


def is_valid_username(username):
    return re.fullmatch("[a-zA-Z0-9_@+.-]*", username) and len(username) > 0 and len(username) <= 150


class SignUp(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=23)
    expiry = models.DateTimeField()


class Settings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    language = models.CharField(max_length=2)
