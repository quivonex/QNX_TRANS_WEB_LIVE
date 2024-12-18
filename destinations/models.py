from django.db import models
from django.core.validators import RegexValidator
from branches.models import BranchMaster
from django.contrib.auth import get_user_model
User = get_user_model()


class DestinationMaster(models.Model):
    id = models.AutoField(primary_key=True)
    destination_name = models.CharField(
        max_length=255, blank=False, unique=True)
    branch = models.ForeignKey(
        BranchMaster, on_delete=models.CASCADE, related_name='destinations')
    pin_code = models.CharField(max_length=10, blank=False, validators=[
        RegexValidator(
            regex='^\\d{6}$',
            message='Pin code must be a 6-digit number.'
        )
    ])
    kilometer = models.PositiveIntegerField(blank=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='destination_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='destination_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'destination_master'
        verbose_name = 'Destination Master'
        verbose_name_plural = 'Destination Masters'

    def __str__(self):
        return self.destination_name or 'Unnamed Destination'

    def save(self, *args, **kwargs):
        # Ensure pin code is numeric and 6 digits
        if not self.pin_code.isdigit() or len(self.pin_code) != 6:
            raise ValueError("Pin code must be a 6-digit number")

        # Extract the request object from kwargs
        request = kwargs.pop('request', None)

        # Set the updated_by field if updating an existing record
        if self.pk and request:
            self.updated_by = request.user
        # Set the created_by field if creating a new record
        elif request:
            self.created_by = request.user

        super(DestinationMaster, self).save(*args, **kwargs)
