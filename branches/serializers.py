from rest_framework import serializers
from .models import BranchMaster, EmployeeType, EmployeeMaster


class BranchMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchMaster
        fields = '__all__'


class EmployeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeType
        fields = '__all__'


class EmployeeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMaster
        fields = '__all__'
