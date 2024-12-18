from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models


EXCLUDED_MODELS = []
EXCLUDED_FIELDS = ['email_id','password','role']

@receiver(pre_save)
def convert_charfields_to_uppercase(sender, instance, **kwargs):
    if not hasattr(sender, '_meta') or sender._meta.abstract:
        return

    # Skip specific models
    if sender.__name__ in EXCLUDED_MODELS:
        return

    for field in sender._meta.fields:
        if (
            isinstance(field, (models.CharField, models.TextField)) and 
            not isinstance(field, models.EmailField) and 
            field.name not in EXCLUDED_FIELDS
        ):
            value = getattr(instance, field.name)
            if value and isinstance(value, str):
                setattr(instance, field.name, value.upper())
