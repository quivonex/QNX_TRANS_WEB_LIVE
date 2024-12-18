# serializers.py
from rest_framework import serializers
from .models import CompanyMaster, FinancialYears, StateMaster, RegionMaster


class CompanyMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyMaster
        fields = '__all__'  # Adjust fields as necessary


class FinancialYearsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialYears
        fields = '__all__'  # Adjust fields as necessary


class StateMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateMaster
        fields = '__all__'  # Adjust fields as necessary


class RegionMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionMaster
        fields = '__all__'  # Adjust fields as necessary
