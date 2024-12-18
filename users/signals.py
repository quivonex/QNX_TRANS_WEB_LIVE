# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.conf import settings
# from .models import UserProfile


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.get_or_create(user=instance)
#     else:
#         # Update existing profile if needed
#         UserProfile.objects.update_or_create(
#             user=instance, defaults={'branch': instance.userprofile.branch})


# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.conf import settings
# from .models import UserProfile


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.get_or_create(user=instance)
#     else:
#         UserProfile.objects.update_or_create(
#             user=instance, defaults={'branch': instance.userprofile.branch})


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create a new UserProfile for the new user
        UserProfile.objects.get_or_create(user=instance)
    else:
        # Update the existing UserProfile if it exists
        user_profile, created = UserProfile.objects.get_or_create(
            user=instance)
        # No need to update anything here, as the profile already exists
