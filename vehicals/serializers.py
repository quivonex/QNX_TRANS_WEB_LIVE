# serializers.py
from rest_framework import serializers
from .models import OwnerMaster, VehicalTypes, VendorTypes, VehicalMaster, DriverMaster


class OwnerMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerMaster
        fields = '__all__'


class VehicalTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicalTypes
        fields = '__all__'


class VendorTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorTypes
        fields = '__all__'


class VehicalMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicalMaster
        fields = '__all__'


class DriverMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverMaster
        fields = '__all__'
