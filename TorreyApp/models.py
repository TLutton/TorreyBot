from django.db import models
from django.contrib.auth.models import User
from django.core.validators import int_list_validator
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Golfer(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    email = models.EmailField()
    num_players = models.IntegerField(default=1)
    send_notifications = models.BooleanField(default=True)
    # Sun -> 1, Mon -> 2, etc..
    days_of_week = models.CharField(validators=[int_list_validator], max_length=30)
    earliest_time = models.PositiveSmallIntegerField(default=6)
    latest_time = models.PositiveSmallIntegerField(default=15)
    # Courses of interest
    torrey_north = models.BooleanField(default=True)
    torrey_south = models.BooleanField(default=True)


# Signals for automatically creating/saving golfer when user is created/saved
@receiver(post_save, sender=User)
def create_golfer(sender, instance, created, **kwargs):
    if created:
        Golfer.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_golfer(sender, instance, **kwargs):
    instance.golfer.save()
    