from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import StandardRate, LR_Bokking, LR_Bokking_Description,LR_Other_Charges  
from branches.models import BranchMaster
from vehicals.models import VehicalMaster
from parties.models import PartyMaster
from items.models import QuotationTypes
from transactions.models import CollectionTypes
from transactions.models import DeliveryTypes
from destinations.models import DestinationMaster
from transactions.models import LoadTypes
from transactions.models import PayTypes
from transactions.models import PaidTypes
from items.models import ItemDetailsMaster
from items.serializers import ItemDetailsMasterSerializer
from collection.models import Collection,BookingMemo,BookingMemoLRs

User = get_user_model()

class StandardRateSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = StandardRate
        fields = [
            'id', 'quotation_date', 'diesel_rate', 'approve_date', 'expiry_date', 'party',
            'from_branch', 'to_branch', 'bilty_charges', 'measurement_type', 'up', 'to', 'rate', 
            'coll_charges', 'del_charges', 'hamali_charges', 'godown_charges', 
            'insurance_charges', 'eway_bill_charges', 'created_by', 'created_at', 
            'updated_by', 'updated_at', 'is_active'
        ]

class LR_BokkingDescriptionSerializer(serializers.ModelSerializer):
    # description = ItemDetailsMasterSerializer()
    actual_weight = serializers.FloatField()
    charged_weight = serializers.FloatField()
    rate = serializers.FloatField()

    class Meta:
        model = LR_Bokking_Description
        fields = [
            'id', 'description', 'quantity', 'actual_weight', 'charged_weight',
            'unit_type', 'rate', 'challan_no', 'inv_value', 'e_way_bill_no'
        ]

# Serializer for LR_Other_Charges
class LR_Other_ChargesSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = LR_Other_Charges
        fields = [
            'id', 'charges_name', 'created_by', 'created_at', 
            'updated_by', 'updated_at', 'is_active', 'flag'
        ]


class LRBokkingSerializer(serializers.ModelSerializer):
    descriptions = LR_BokkingDescriptionSerializer(many=True, read_only=True)
    # created_by = serializers.StringRelatedField()
    # updated_by = serializers.StringRelatedField()

    class Meta:
        model = LR_Bokking
        fields = [
            'lr_no', 'branch','lr_number', 'date', 'coll_vehicle', 'tran_vehicle', 'del_vehicle', 
            'remark', 'from_branch', 'to_branch', 'consignor', 'consignee', 'pay_type', 
            'billing_party', 'load_type', 'type', 'coll_type', 'del_type', 'coll_at', 
            'del_at','coll_km','del_km', 'descriptions', 'freight', 'e_way_bill_charges', 'collection', 
            'door_delivery', 'toll_escort_total', 'bilty_charges', 'hamali', 
            'godown_charges', 'insurance_charges', 'total', 'other_charge_1','other_charge_1_val',
            'other_charge_2','other_charge_2_val', 'fuel_surcharge', 
            'grand_total','tchargedwt','tpackage','okpackage', 'created_by', 'created_at', 'updated_by', 'updated_at', 'is_active'
        ]

class BookingMemoLRsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingMemoLRs
        fields = '__all__'

class BookingMemoSerializer(serializers.ModelSerializer):
    lr_list = BookingMemoLRsSerializer(many=True)  # Serialize the related BookingMemoLRs

    class Meta:
        model = BookingMemo
        fields = '__all__'

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'