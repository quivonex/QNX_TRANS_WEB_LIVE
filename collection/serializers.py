from rest_framework import serializers

from branches.models import BranchMaster
from destinations.models import DestinationMaster
from lr_booking.models import LR_Bokking
from lr_booking.serializers import LRBokkingSerializer
from vehicals.models import DriverMaster, VehicalMaster, VehicalTypes
from .models import  BookingMemo, BookingMemoLRs, Collection,TripBokkingMemos,TripMemo,TripMode,VehicalHireContract,BrokerMasterTrips,BrokerMaster

class CollectionSerializer(serializers.ModelSerializer):
    # lr_booking = serializers.PrimaryKeyRelatedField(queryset=LR_Bokking.objects.all(), many=True)
    lr_booking = LRBokkingSerializer(many=True, read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Collection
        fields = [
            'id', 'branch_name', 'memo_no', 'date', 'vehical_no', 'driver_name', 'contact',
            'vehical_type','vehicle_capacity', 'from_branch', 'to_branch', 'memo_status', 'memo_remarks',
            'lr_booking', 'total_weight', 'total_collection', 'extra_amt', 'hamali',
            'union_charges', 'total_amt', 'advance', 'balance', 'created_by',
            'created_at', 'updated_by', 'updated_at', 'is_active'
        ]

    # def create(self, validated_data):
    #     lr_booking_data = validated_data.pop('lr_booking', [])
    #     collection = Collection.objects.create(**validated_data)
        
    #     # Add lr_booking to the collection after creation
    #     collection.lr_booking.set(lr_booking_data)
    #     return collection

class BookingMemoLRsSerializer(serializers.ModelSerializer):
    lr_booking = LRBokkingSerializer(read_only=True)
    class Meta:
        model = BookingMemoLRs
        fields = [
            'id', 'lr_booking', 'coll_point', 'del_point', 'lr_remarks', 
            'created_by', 'created_at', 'updated_by', 'updated_at', 'is_active'
        ]

class BookingMemoSerializer(serializers.ModelSerializer):
    lr_list = BookingMemoLRsSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()


    class Meta:
        model = BookingMemo
        fields = [
            'id', 'branch_name', 'memo_no', 'date', 'trip_no', 'vehicle_trip_route',
            'vehical_no','vehicle_capacity', 'driver_name', 'contact_no', 'owner_name', 'from_branch',
            'to_branch', 'memo_status', 
            'vehical_type','km', 'memo_remarks', 'lr_list', 'lr_qty', 'total_weight',
            'created_by', 'created_at', 'updated_by', 'updated_at', 'is_active'
        ]

class TripModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripMode
        fields = [
            'id', 'mode_name',
            'created_by', 'created_at', 'updated_by', 'updated_at', 'is_active'
        ]


class TripBokkingMemosSerializer(serializers.ModelSerializer):
    booking_memo = BookingMemoSerializer(read_only=True)
    class Meta:
        model = TripBokkingMemos
        fields = [
            'id', 'booking_memo', 'remark', 
            'created_by', 'created_at', 'updated_by', 'updated_at', 'is_active'
        ]


class VehicalHireContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicalHireContract
        fields = '__all__'

class TripMemoSerializer(serializers.ModelSerializer):
    booking_memos = TripBokkingMemosSerializer(many=True, read_only=True)
    # created_by = serializers.StringRelatedField()
    # updated_by = serializers.StringRelatedField()

    class Meta:
        model = TripMemo
        fields = [
            'id', 'branch', 'trip_no', 'trip_mode', 'date', 'vehicle_no',
            'driver_name', 'contact_no',
            'from_branch', 'to_branch', 'trip_memo_status', 'remark', 
            'booking_memos', 'km','total_qty','basic_lorry_frights','total_lorry_frights','balance_lorry_frights','total_weight','toll_escort','hamali','other_charger','actual_vehicle_hire','vehicle_hire','waiting','less_advance','less_diesel_amt','less_topay_amt','total_vehicle_hire','balance_vehicle_hire',
            'created_by', 'created_at', 'updated_by', 'updated_at', 'is_active'
        ]


class BrokerMasterTripsSerializer(serializers.ModelSerializer):
    trip_memo = TripMemoSerializer(read_only=True)
    class Meta:
        model = BrokerMasterTrips
        fields = '__all__'


class BrokerMasterSerializer(serializers.ModelSerializer):
    trip_details = BrokerMasterTripsSerializer(many=True, read_only=True)    
    class Meta:
        model = BrokerMaster
        fields = '__all__'
