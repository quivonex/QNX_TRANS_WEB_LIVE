from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.db import models
from branches.models import BranchMaster  
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class UserProfile(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branches = models.ManyToManyField(
        BranchMaster, related_name='user_profiles')
    role = models.CharField(max_length=50, choices=[('admin', 'admin'), ('region_manager', 'region_manager'),('branch_manager','branch_manager')], default='branch_manager')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        branch_names = ', '.join(
            branch.branch_name for branch in self.branches.all())
        return f'{self.user.username} - {branch_names or "No Branches"}'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Check if the UserProfile exists before saving
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
        else:
            UserProfile.objects.create(user=instance)
