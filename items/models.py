from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ItemDetailsMaster(models.Model):
    id = models.AutoField(primary_key=True)
    item_name = models.CharField(
        max_length=255, unique=True, blank=False)  # Unique item name
    # Optional description field
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='item_details_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='item_details_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'item_details_master'  # Changed to match model name
        verbose_name = 'Item Detail'
        verbose_name_plural = 'Item Details'

    def __str__(self):
        return self.item_name or 'Unnamed Item'

    def save(self, *args, **kwargs):
        # Extract the request object from kwargs
        request = kwargs.pop('request', None)

        # Set the updated_by field if updating an existing record
        if self.pk and request:
            self.updated_by = request.user
        # Set the created_by field if creating a new record
        elif request:
            self.created_by = request.user

        # Call the superclass save method
        super(ItemDetailsMaster, self).save(*args, **kwargs)


class QuotationTypes(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)  # Unique item name
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='quotation_types_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotation_types_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'quotation_types'  # Changed to match model name
        verbose_name = 'Quotation Types'
        verbose_name_plural = 'Quotation Types'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        # Extract the request object from kwargs
        request = kwargs.pop('request', None)

        # Set the updated_by field if updating an existing record
        if self.pk and request:
            self.updated_by = request.user
        # Set the created_by field if creating a new record
        elif request:
            self.created_by = request.user

        # Call the superclass save method
        super(QuotationTypes, self).save(*args, **kwargs)
