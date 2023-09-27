from django.db import models


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
