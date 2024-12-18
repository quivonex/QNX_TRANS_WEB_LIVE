from rest_framework import serializers
from .models import LoadTypes, PaidTypes, PayTypes, CollectionTypes, DeliveryTypes


class LoadTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoadTypes
        fields = ['id', 'type_name', 'created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']


class PaidTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaidTypes
        fields = ['id', 'type_name', 'created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']


class PayTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayTypes
        fields = ['id', 'type_name', 'created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']


class CollectionTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionTypes
        fields = ['id', 'type_name', 'created_by', 'created_at', 'updated_by', 'updated_at', 'is_active',]
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']


class DeliveryTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryTypes
        fields = ['id', 'type_name', 'created_by', 'created_at', 'updated_by', 'updated_at', 'is_active']
        read_only_fields = ['created_by', 'created_at', 'updated_by', 'updated_at']
