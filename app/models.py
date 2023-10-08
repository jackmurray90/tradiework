from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import re


def is_valid_username(username):
    return re.fullmatch("[a-zA-Z0-9_@+.-]*", username) and len(username) > 0 and len(username) <= 150


class SignUp(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=23)
    expiry = models.DateTimeField()


class Language(models.Model):
    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=200)


class String(models.Model):
    english = models.TextField()
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    translation = models.TextField()
    in_use = models.BooleanField()


class Settings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)


@receiver(post_save, sender=User)
def create_settings(sender, instance, created, **kwargs):
    if created:
        Settings.objects.create(user=instance)
