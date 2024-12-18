from rest_framework import serializers
from lr_booking.serializers import LRBokkingSerializer
from .models import TruckUnloadingReportStatus,TruckUnloadingReportDetails,TruckUnloadingReport, LocalMemoDelivery, DeliveryStatement,CustomerOutstanding
from collection.serializers import BookingMemoSerializer

class TruckUnloadingReportStatusSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = TruckUnloadingReportStatus
        fields = '__all__'

class TruckUnloadingReportDetailsSerializer(serializers.ModelSerializer):
    lr_booking = LRBokkingSerializer(read_only=True)
    status = TruckUnloadingReportStatusSerializer(read_only=True)
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = TruckUnloadingReportDetails
        fields = '__all__'

class TruckUnloadingReportSerializer(serializers.ModelSerializer):
    tur_details = TruckUnloadingReportDetailsSerializer(many=True,read_only=True)
    memo_no = BookingMemoSerializer(read_only=True)
    class Meta:
        model = TruckUnloadingReport
        fields = '__all__'
    
class LocalMemoDeliverySerializer(serializers.ModelSerializer):
    lr_booking = LRBokkingSerializer(many=True, read_only=True)
   

    class Meta:
        model = LocalMemoDelivery
        fields = '__all__'

class DeliveryStatementSerializer(serializers.ModelSerializer):
    lr_booking = LRBokkingSerializer(many=True, read_only=True)
    class Meta:
        model = DeliveryStatement
        fields = '__all__'

class CustomerOutstandingSerializer(serializers.ModelSerializer):
    lr_booking = LRBokkingSerializer(many=True, read_only=True)
    class Meta:
        model = CustomerOutstanding
        fields = '__all__'