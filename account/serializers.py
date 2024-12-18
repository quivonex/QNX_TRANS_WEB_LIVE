from rest_framework import serializers
from .models import GSTMaster, PartyBilling, VoucherReceiptType, VoucherReceiptBranch, MoneyReceipt,VoucherPaymentBranch,VoucherPaymentType,CashBook,BillingSubmission,DeductionReasonType,Deduction
from lr_booking.serializers import LRBokkingSerializer
from vehicals.serializers import VehicalMasterSerializer,DriverMasterSerializer
from branches.serializers import EmployeeMasterSerializer
from collection.serializers import CollectionSerializer,BookingMemoSerializer,TripMemoSerializer
from delivery.serializers import LocalMemoDeliverySerializer
from vehicals.models import VehicalMaster,DriverMaster
from branches.models import EmployeeMaster
from collection.models import Collection,BookingMemo,TripMemo
from delivery.models import LocalMemoDelivery
from parties.models import PartyMaster
from lr_booking.models import LR_Bokking

class GSTMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = GSTMaster
        fields = '__all__'


class PartyBillingSerializer(serializers.ModelSerializer):
    lr_booking = LRBokkingSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = PartyBilling
        fields = '__all__'

class VoucherReceiptTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherReceiptType
        fields = '__all__'

class VoucherReceiptBranchSerializer(serializers.ModelSerializer):
    lr_booking = LRBokkingSerializer(many=True, read_only=True)
    party_billing = PartyBillingSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = VoucherReceiptBranch
        fields = '__all__'

class MoneyReceiptSerializer(serializers.ModelSerializer):
    lr_booking = LRBokkingSerializer(many=True, read_only=True)
    party_billing = PartyBillingSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = MoneyReceipt
        fields = '__all__'

class VoucherPaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoucherPaymentType
        fields = '__all__'

class VoucherPaymentBranchSerializer(serializers.ModelSerializer):
    # Define fields dynamically for retrieval
    vehical_no = serializers.PrimaryKeyRelatedField(queryset=VehicalMaster.objects.all(), required=False, allow_null=True)
    lr_no = serializers.PrimaryKeyRelatedField(queryset=LR_Bokking.objects.all(), required=False, allow_null=True)
    employee = serializers.PrimaryKeyRelatedField(queryset=EmployeeMaster.objects.all(), required=False, allow_null=True)
    party = serializers.PrimaryKeyRelatedField(queryset=PartyMaster.objects.all(), required=False, allow_null=True)
    lcm_no = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all(), required=False, allow_null=True)
    booking_memo = serializers.PrimaryKeyRelatedField(queryset=BookingMemo.objects.all(), required=False, allow_null=True)
    driver = serializers.PrimaryKeyRelatedField(queryset=DriverMaster.objects.all(), required=False, allow_null=True)
    ldm_no = serializers.PrimaryKeyRelatedField(queryset=LocalMemoDelivery.objects.all(), required=False, allow_null=True)
    trip_no = serializers.PrimaryKeyRelatedField(queryset=TripMemo.objects.all(), required=False, allow_null=True)

    class Meta:
        model = VoucherPaymentBranch
        fields = '__all__'

    def to_representation(self, instance):
        """Customize the representation of the serialized data."""
        data = super().to_representation(instance)
        # Include full object details for retrieve purposes
        data['vehical_no'] = VehicalMasterSerializer(instance.vehical_no).data if instance.vehical_no else None
        data['lr_no'] = LRBokkingSerializer(instance.lr_no).data if instance.lr_no else None
        data['employee'] = EmployeeMasterSerializer(instance.employee).data if instance.employee else None
        data['party'] = PartyBillingSerializer(instance.party).data if instance.party else None
        data['lcm_no'] = CollectionSerializer(instance.lcm_no).data if instance.lcm_no else None
        data['booking_memo'] = BookingMemoSerializer(instance.booking_memo).data if instance.booking_memo else None
        data['driver'] = DriverMasterSerializer(instance.driver).data if instance.driver else None
        data['ldm_no'] = LocalMemoDeliverySerializer(instance.ldm_no).data if instance.ldm_no else None
        data['trip_no'] = TripMemoSerializer(instance.trip_no).data if instance.trip_no else None
        return data


class CashBookSerializer(serializers.ModelSerializer):    
    credit = VoucherReceiptBranchSerializer(many=True, read_only=True) 
    debit = VoucherPaymentBranchSerializer(many=True, read_only=True)  

    class Meta:
        model = CashBook
        fields = '__all__'

class BillingSubmissionSerializer(serializers.ModelSerializer): 
    bill_no = serializers.PrimaryKeyRelatedField(queryset=PartyBilling.objects.all(), required=False)

    class Meta:
        model = BillingSubmission
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['bill_no'] = PartyBillingSerializer(instance.bill_no).data if instance.bill_no else None
        return data

class DeductionReasonTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeductionReasonType
        fields = '__all__'

class DeductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deduction
        fields = '__all__'