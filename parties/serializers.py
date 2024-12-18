from rest_framework import serializers
from .models import PartyTypes, PartyMaster
from branches.models import BranchMaster
from destinations.models import DestinationMaster


class PartyTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartyTypes
        fields = '__all__'


class PartyMasterSerializer(serializers.ModelSerializer):
    party_type = serializers.PrimaryKeyRelatedField(
        queryset=PartyTypes.objects.all(), required=False)
    area = serializers.PrimaryKeyRelatedField(
        queryset=DestinationMaster.objects.all())
    branch = serializers.PrimaryKeyRelatedField(
        queryset=BranchMaster.objects.all())

    class Meta:
        model = PartyMaster
        fields = [
            'id', 'party_type','pay_type', 'party_name', 'address', 'area', 'contact_no',
            'email_id','gst_no', 'pincode', 'branch', 'credit_period','credit_amount', 'po_no',
            'vendor_code', 'quotation_number','party_weekly_off', 'created_by', 'created_at',
            'updated_by', 'updated_at', 'is_active'
        ]
