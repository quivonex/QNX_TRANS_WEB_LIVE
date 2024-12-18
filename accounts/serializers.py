from rest_framework import serializers
from .models import EffectTypes, PaymentTypes, ReceiptTypes
from django.contrib.auth import get_user_model

User = get_user_model()

# Serializer for the EffectTypes model
class EffectTypesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EffectTypes
        fields = '__all__'

# Serializer for the ReceiptTypes model
class ReceiptTypesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReceiptTypes
        fields = '__all__'

# Serializer for the ReceiptTypes model
class PaymentTypesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PaymentTypes
        fields = '__all__'
