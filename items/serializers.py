from rest_framework import serializers
from .models import ItemDetailsMaster, QuotationTypes
from django.contrib.auth import get_user_model

User = get_user_model()

class ItemDetailsMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemDetailsMaster
        fields = '__all__' 
    


class QuotationTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationTypes
        fields = '__all__' 

    
