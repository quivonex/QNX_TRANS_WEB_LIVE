from django.db import models
from django.contrib.auth.models import User
from branches.models import BranchMaster 
from collection.models import BookingMemo
from destinations.models import DestinationMaster
from lr_booking.models import LR_Bokking
from vehicals.models import VehicalMaster,DriverMaster
from django.core.validators import MinValueValidator, MaxValueValidator
from parties.models import PartyMaster

class TruckUnloadingReportStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=50, unique=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='tur_status_created_by', default=1
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tur_status_updated_by'
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'truck_unloading_report_status'

    def __str__(self):
        return f"{self.status} - {self.id}"
    
class TruckUnloadingReportDetails(models.Model):
    id = models.AutoField(primary_key=True)
    lr_booking = models.ForeignKey(LR_Bokking,on_delete=models.SET_NULL, null=True, related_name='tur_details_lr')
    status = models.ForeignKey(TruckUnloadingReportStatus, on_delete=models.SET_NULL, null=True, blank=True)
    okpackage = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,default=0)
    ngpackage = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,default=0)
    remark = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='tur_details_created_by', default=1
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tur_details_updated_by'
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'truck_unloading_report_details'

    def __str__(self):
        return f"{self.id} - {self.remark}"

class TruckUnloadingReport(models.Model):
    id = models.AutoField(primary_key=True)
    branch_name = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, null=True, blank=True)
    tur_no = models.CharField(max_length=10, unique=True)
    date = models.DateField()
    memo_no = models.ForeignKey(BookingMemo, on_delete=models.SET_NULL, null=True, blank=True)
    tur_details = models.ManyToManyField(TruckUnloadingReportDetails, blank=True)
    tur_remark = models.CharField(max_length=100, blank=True, null=True)
    total_qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, default=0)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='tur_created_by', default=1
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tur_updated_by'
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)
    printed_by_branch_manager = models.BooleanField(default=False)

    class Meta:
        db_table = 'truck_unloading_report'

    def __str__(self):
        return f"{self.tur_no} - {self.date}"

class LocalMemoDelivery(models.Model):
    id = models.AutoField(primary_key=True)
    branch_name = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, null=True, blank=True, related_name='ldm_branch')
    memo_no = models.CharField(max_length=10, unique=True)
    date = models.DateField()
    vehical_no = models.ForeignKey(VehicalMaster, on_delete=models.SET_NULL, null=True, blank=True)
    driver_name = models.ForeignKey(DriverMaster, on_delete=models.SET_NULL, null=True, blank=True)
    from_branch = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, null=True, blank=True)
    to_branch = models.ForeignKey(DestinationMaster, on_delete=models.SET_NULL, null=True, blank=True)
    memo_status = models.CharField(max_length=50, choices=[('OK', 'OK'), ('CANCEL', 'CANCEL')], default='OK')
    memo_remarks = models.CharField(max_length=100, blank=True, null=True)
    lr_booking = models.ManyToManyField(LR_Bokking, related_name='delivery_lr_bookings', blank=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2)
    total_delivery = models.DecimalField(max_digits=10, decimal_places=2)
    extra_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    hamali = models.IntegerField(default=0)
    union_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amt = models.IntegerField(default=0)
    advance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default=1, related_name='lmd_created_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)
    printed_by_branch_manager = models.BooleanField(default=False)

    class Meta:
        db_table = 'local_memo_delivery'

    def __str__(self):
        return f"{self.memo_no} - {self.date}"
    
class DeliveryStatement(models.Model):
    id = models.AutoField(primary_key=True)
    branch_name = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_no = models.CharField(max_length=10, unique=True)
    date = models.DateField()
    lr_booking = models.ManyToManyField(LR_Bokking, related_name='ds_lr_bookings', blank=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    lr_qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default=1, related_name='nds_created_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)
    printed_by_branch_manager = models.BooleanField(default=False)

    class Meta:
        db_table = 'delivery_statement'

    def __str__(self):
        return f"{self.delivery_no} - {self.date}"
    

class CustomerOutstanding(models.Model):
    billing_party = models.ForeignKey(
        PartyMaster, related_name='custom_billing_party', on_delete=models.SET_NULL, null=True
    )
    lr_booking = models.ManyToManyField(
        LR_Bokking, related_name='custom_lr_bookings', blank=True
    )
    credit_amount = models.PositiveIntegerField(blank=True, null=True)
    credit_period = models.PositiveIntegerField(
        blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(365)]
    )
    last_credit_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_outstanding'
    
    def __str__(self):
        return f"{self.billing_party} - Outstanding"

