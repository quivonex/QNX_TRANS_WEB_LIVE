# Create your models here.
from django.contrib.auth import get_user_model
from django.db import models
from django.forms import ValidationError
from branches.models import BranchMaster
from vehicals.models import VehicalMaster,DriverMaster,VehicalTypes,OwnerMaster
from destinations.models import DestinationMaster
from lr_booking.models import LR_Bokking
from transactions.models import LoadTypes, PaidTypes, PayTypes, CollectionTypes, DeliveryTypes
from routes.models import RouteMaster

User = get_user_model()

#Local collection memo
class Collection(models.Model):
        
    STATUS_OK = 'OK'
    STATUS_CANCEL = 'CANCEL'
    MEMO_STATUS_CHOICES = [
        (STATUS_OK, 'OK'),
        (STATUS_CANCEL, 'CANCEL')
    ]
    
    # branch_name = models.CharField(max_length=100)
    branch_name = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, related_name='collections_branch', null=True, blank=True)
    memo_no = models.CharField(max_length=10,unique=True) 
    date = models.DateField()
    # vehicle_no = models.CharField(max_length=50)
    vehical_no = models.ForeignKey(VehicalMaster, on_delete=models.SET_NULL, related_name='collections_vehical_no', null=True, blank=True)
    driver_name = models.ForeignKey(DriverMaster, on_delete=models.SET_NULL, related_name='collections_driver_no', null=True, blank=True)
    contact = models.CharField(max_length=15, blank=True, null=True) 
    vehical_type = models.ForeignKey(VehicalTypes, on_delete=models.SET_NULL, related_name='collections_vehicle_type', null=True, blank=True)
    vehicle_capacity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    from_branch = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, related_name='origin_collections_from_branch', null=True, blank=True)
    to_branch = models.ForeignKey(DestinationMaster, on_delete=models.SET_NULL, related_name='destination_collections_to_branch', null=True, blank=True)
    # memo_status = models.CharField(max_length=50)    #which type of choices
    memo_status = models.CharField(max_length=50, choices=[('OK', 'OK'), ('CANCEL', 'CANCEL')], default='OK')
    memo_remarks = models.CharField(max_length=100, blank=True, null=True)

    lr_booking = models.ManyToManyField(LR_Bokking, related_name='collections_lr_bookings', blank=True)

    total_weight = models.DecimalField(max_digits=10, decimal_places=2)
    total_collection = models.DecimalField(max_digits=10, decimal_places=2)
    extra_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True,null=True)
    hamali = models.IntegerField(blank=True,null=True) 
    union_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True,null=True)
    total_amt = models.IntegerField()
    advance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True,null=True)
    balance = models.IntegerField() 

    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='collection_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collection_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)
    printed_by_branch_manager = models.BooleanField(default=False)

    class Meta:
        db_table = 'collection_memo'
    
    def __str__(self):
        return f"{self.memo_no} - {self.branch_name}"
    
class BookingMemoLRs(models.Model):
    lr_booking = models.ForeignKey(LR_Bokking,on_delete=models.SET_NULL, null=True, related_name='booking_memo_lr')
    coll_point = models.ForeignKey(
        CollectionTypes, related_name='booking_memo_lr_collection_type', on_delete=models.SET_NULL, null=True)
    del_point = models.ForeignKey(
        DeliveryTypes, related_name='booking_memo_lr_delivery_type', on_delete=models.SET_NULL, null=True)
    lr_remarks = models.CharField(max_length=100, blank=True, null=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='booking_memo_lr_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='booking_memo_lr_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'booking_memo_lrs'
    
    def __str__(self):
        return f"{self.id}"

class BookingMemo(models.Model):
    STATUS_OK = 'Ok'
    STATUS_CANCEL = 'CANCEL'
    MEMO_STATUS_CHOICES = [
        (STATUS_OK, 'OK'),
        (STATUS_CANCEL, 'CANCEL')
    ]
    id = models.AutoField(primary_key=True)
    branch_name = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, related_name='booking_memos', null=True, blank=True)
    memo_no = models.CharField(max_length=10,unique=True)
    date = models.DateField()
    memo_mode = models.CharField(max_length=50, choices=[('OPEN', 'OPEN'), ('CLOSE', 'CLOSE')], default='OPEN')
    trip_no = models.CharField(max_length=50, blank=True, null=True)
    vehicle_trip_route = models.ForeignKey(RouteMaster, on_delete=models.SET_NULL, null=True,blank=True)

    vehical_no = models.ForeignKey(VehicalMaster, on_delete=models.SET_NULL, related_name='booking_memos', null=True, blank=True)
    vehicle_capacity = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    driver_name = models.ForeignKey(DriverMaster, on_delete=models.SET_NULL, related_name='booking_memos', null=True, blank=True)
    contact_no = models.TextField(blank=True)
    
    owner_name = models.ForeignKey(OwnerMaster, on_delete=models.SET_NULL, related_name='booking_memos', null=True, blank=True)

    from_branch = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, related_name='origin_booking_memos', null=True, blank=True)
    to_branch = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, related_name='destination_booking_memos', null=True, blank=True)
    

    memo_status = models.CharField(max_length=50, choices=[('OK', 'OK'), ('CANCEL', 'CANCEL')], default='OK')
    vehical_type = models.ForeignKey(VehicalTypes, on_delete=models.SET_NULL, related_name='booking_memos', null=True, blank=True)
    km = models.FloatField(null=True, blank=True)
    memo_remarks = models.CharField(max_length=100, blank=True, null=True)

    lr_list = models.ManyToManyField(BookingMemoLRs, related_name='booking_memo_booking_memo_lrs', blank=True)
    
    lr_qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)    
    total_weight = models.DecimalField(max_digits=10, decimal_places=2)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='booking_memo_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='booking_memo_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)
    printed_by_branch_manager = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'booking_memo'

    def __str__(self):
        return f"BookingMemo {self.id} - {self.memo_status}"

    def clean(self):
        # Custom validation for contact_no and email_id fields
        contact_numbers = self.contact_no.split(',')

        # Validate each contact number (exactly 10 digits only)
        for number in contact_numbers:
            number = number.strip()  # Remove extra whitespace
            if number:
                # Check if the number is exactly 10 digits
                if not number.isdigit() or len(number) != 10:
                    raise ValidationError(f"Invalid contact number format: {number}. It must be exactly 10 digits.")

    def save(self, *args, **kwargs):
        # Call the clean method to perform validation
        self.clean()
        
        # Call the superclass save method
        super(BookingMemo, self).save(*args, **kwargs)

class TripMode(models.Model):
    mode_name = models.CharField(max_length=100)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='TripMode_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='TripMode_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'trip_mode'

    def __str__(self):
        return self.mode_name

class VehicalHireContract(models.Model):
    from_branch = models.ForeignKey(
        BranchMaster, related_name='hire_contract_rate_from_branch', on_delete=models.CASCADE
    )
    to_branch = models.ForeignKey(
        BranchMaster, related_name='hire_contract_rate_to_branch', on_delete=models.CASCADE
    )
    vehical_type = models.ForeignKey(
        VehicalTypes, related_name='hire_contract_rate_vehical_type', on_delete=models.CASCADE,null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2)      
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='hire_contract_rate_created_by', default=1
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hire_contract_rate_updated_by'
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  
    flag = models.BooleanField(default=True) 

    class Meta:
        db_table = 'vehical_hire_contract'  

    def __str__(self):
        return f"Contract: {self.from_branch} to {self.to_branch} ({self.from_kg}kg - {self.to_kg}kg)"

class TripMemo(models.Model):
    STATUS_OK = 'OK'
    STATUS_NOT_OK = 'CANCEL'
    TRIP_MEMO_STATUS_CHOICES = [
        (STATUS_OK, 'OK'),
        (STATUS_NOT_OK, 'CANCEL'),
    ]

    branch = models.ForeignKey(
        BranchMaster, on_delete=models.SET_NULL, related_name='TripMemo_branch', null=True)
    trip_no = models.CharField(max_length=10, unique=True, null=True)
    date = models.DateField()
    trip_mode = models.CharField(max_length=50, choices=[('OPEN', 'OPEN'), ('CLOSE', 'CLOSE')], default='OPEN')
    vehicle_no = models.ForeignKey(VehicalMaster, on_delete=models.SET_NULL, null=True)
    driver_name = models.ForeignKey(DriverMaster, on_delete=models.SET_NULL, null=True)
    contact_no = models.TextField(blank=False)
    from_branch = models.ForeignKey(
        BranchMaster, related_name='TripMemo_from_branch', on_delete=models.SET_NULL, null=True)
    to_branch = models.ForeignKey(
        BranchMaster, related_name='TripMemo_to_branch', on_delete=models.SET_NULL, null=True)
    trip_memo_status = models.CharField(
        max_length=10, choices=TRIP_MEMO_STATUS_CHOICES, default=STATUS_OK)
    remark = models.CharField(max_length=100, blank=True)
    booking_memos = models.ManyToManyField('TripBokkingMemos', blank=True)

    km = models.FloatField(null=True, blank=True)
    total_qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  

    basic_lorry_frights = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    total_lorry_frights = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    balance_lorry_frights = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    total_weight = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    toll_escort = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    hamali = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    other_charger = models.DecimalField(max_digits=10, decimal_places=2,default=0)    

    actual_vehicle_hire = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    vehicle_hire = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    waiting = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    less_advance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    less_diesel_amt = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    less_topay_amt = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    total_vehicle_hire = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    balance_vehicle_hire = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='TripMemo_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='TripMemo_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)
    printed_by_branch_manager = models.BooleanField(default=False)

    class Meta:
        db_table = 'trip_memo'

    def clean(self):
        # Custom validation for contact_no and email_id fields
        contact_numbers = self.contact_no.split(',')

        # Validate each contact number (exactly 10 digits only)
        for number in contact_numbers:
            number = number.strip()  # Remove extra whitespace
            if number:
                # Check if the number is exactly 10 digits
                if not number.isdigit() or len(number) != 10:
                    raise ValidationError(f"Invalid contact number format: {number}. It must be exactly 10 digits.")

    def __str__(self):
        return f"TripMemo {self.trip_no} - {self.trip_memo_status}"

    def save(self, *args, **kwargs):
        # Call the clean method to perform validation
        self.clean()
        
        # Call the superclass save method
        super(TripMemo, self).save(*args, **kwargs)

class TripBokkingMemos(models.Model):
    booking_memo = models.ForeignKey('BookingMemo', on_delete=models.SET_NULL, null=True)
    remark = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='trip_bokking_memos_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='trip_bokking_memos_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'trip_bokking_memos'

    def __str__(self):
        return f"TripBokkingMemos {self.id}"

class BrokerMasterTrips(models.Model):
    trip_memo = models.ForeignKey('TripMemo', on_delete=models.SET_NULL, null=True)
    advance = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2,default=0,null=True,blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='broker_master_trip_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='broker_master_trip_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'broker_master_trips'

    def __str__(self):
        return f"BrokerMasterTrips {self.id}"

class BrokerMaster(models.Model):
    owner = models.ForeignKey(
        OwnerMaster, related_name='broker_master_owners', on_delete=models.SET_NULL, null=True
    )
    trip_details = models.ManyToManyField(
        BrokerMasterTrips, related_name='broker_master_trip', blank=True
    )  
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='broker_master_created_by', default=1)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='broker_master_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'broker_master'
    
    def __str__(self):
        return f"{self.owner} - Reports"


