from django.db import models
from django.contrib.auth.models import User
import re


def is_valid_username(username):
    return re.fullmatch("[a-zA-Z0-9_@+.-]*", username) and len(username) <= 150


class SignUp(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=23)
    expiry = models.DateTimeField()


class Interest(models.Model):
    TYPE_CHOICES = [
        ("dj", "DJ"),
        ("band", "Band"),
        ("act", "Live act"),
        ("venue", "Venue"),
        ("festival", "Festival"),
        ("event", "Event organizer"),
    ]
    type = models.CharField(max_length=200, choices=TYPE_CHOICES)
    name = models.CharField(max_length=200)
    email = models.EmailField()
