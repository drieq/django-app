from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        default_group, _ = Group.objects.get_or_create(name="Photographers")
        instance.groups.add(default_group)