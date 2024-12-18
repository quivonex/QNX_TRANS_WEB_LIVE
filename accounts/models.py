from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class EffectTypes(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='effect_types_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='effect_types_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'effect_types'
        verbose_name = 'Effect Types'
        verbose_name_plural = 'Effect Types'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user
        super(EffectTypes, self).save(*args, **kwargs)


class PaymentTypes(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)
    effect = models.ForeignKey(EffectTypes, on_delete=models.SET_NULL,
                               null=True, related_name='effect_type_of_payment')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='payment_types_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_types_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'payment_types'
        verbose_name = 'Payment Types'
        verbose_name_plural = 'Payment Types'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user
        super(PaymentTypes, self).save(*args, **kwargs)


class ReceiptTypes(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='receipt_types_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='receipt_types_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'receipt_types'
        verbose_name = 'Receipt Types'
        verbose_name_plural = 'Receipt Types'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user
        super(ReceiptTypes, self).save(*args, **kwargs)
