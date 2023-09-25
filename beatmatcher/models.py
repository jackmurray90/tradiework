from django.db import models


class Interest(models.Model):
    TYPE_CHOICES = [
        ("dj", "DJ"),
        ("venue", "Venue"),
    ]
    type = models.CharField(max_length=5, choices=TYPE_CHOICES)
    name = models.CharField(max_length=200)
    email = models.EmailField()
