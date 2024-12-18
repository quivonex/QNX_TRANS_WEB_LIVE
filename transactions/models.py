from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class LoadTypes(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='load_types_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='load_types_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'load_types'
        verbose_name = 'Load Types'
        verbose_name_plural = 'Load Types'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user
        super(LoadTypes, self).save(*args, **kwargs)


class PaidTypes(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='paid_types_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='paid_types_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'paid_types'
        verbose_name = 'Paid Types'
        verbose_name_plural = 'Paid Types'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user
        super(PaidTypes, self).save(*args, **kwargs)


class PayTypes(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='pay_types_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pay_types_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'pay_types'
        verbose_name = 'Pay Types'
        verbose_name_plural = 'Pay Types'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user
        super(PayTypes, self).save(*args, **kwargs)


class CollectionTypes(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='collection_types_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collection_types_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_show_booking_memo = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'collection_types'
        verbose_name = 'Collection Types'
        verbose_name_plural = 'Collection Types'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user
        super(CollectionTypes, self).save(*args, **kwargs)


class DeliveryTypes(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='delivery_types_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_types_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_show_booking_memo = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'delivery_types'
        verbose_name = 'Delivery Types'
        verbose_name_plural = 'Delivery Types'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user
        super(DeliveryTypes, self).save(*args, **kwargs)
