# models.py

from django.contrib.auth import get_user_model
from django.db import models
from django.forms import ValidationError
from branches.models import BranchMaster
from items.models import QuotationTypes, ItemDetailsMaster
from vehicals.models import VehicalMaster,DriverMaster  
from parties.models import PartyMaster
from accounts.models import PaymentTypes
from destinations.models import DestinationMaster
from transactions.models import LoadTypes, PaidTypes, PayTypes, CollectionTypes, DeliveryTypes
from django.core.validators import RegexValidator,MinValueValidator
User = get_user_model()
from django.db.models import Q

class StandardRate(models.Model):
    id = models.AutoField(primary_key=True)
    quotation_date = models.DateField()
    diesel_rate = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    approve_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    party = models.ForeignKey(
        PartyMaster, related_name='billing_party_of_s_r', on_delete=models.SET_NULL, null=True,blank=True)
    from_branch = models.ForeignKey(
        BranchMaster, related_name='standard_rate_from_branch', on_delete=models.CASCADE)
    to_branch = models.ForeignKey(
        BranchMaster, related_name='standard_rate_to_branch', on_delete=models.CASCADE)
    
    # Renamed 'measurement' to 'measurement_type'
    measurement_type = models.ForeignKey(
        QuotationTypes, related_name='standard_rate_measurement_type', on_delete=models.CASCADE,default=2)
    
    up = models.FloatField()
    to = models.FloatField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    coll_charges = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    del_charges = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    
    # Minimum value validation for hamali_charges
    hamali_charges = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.15)])
    
    godown_charges = models.DecimalField(max_digits=10, decimal_places=2, default=20.00)
    insurance_charges = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    eway_bill_charges = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    
    # Added bilty_charges with default value
    bilty_charges = models.DecimalField(max_digits=10, decimal_places=2, default=70.00)
    
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='standard_rate_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='standard_rate_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'standard_rate'

    def __str__(self):
        return f"{self.id} - {self.rate}"

    def save(self, *args, **kwargs):
        # Set fixed values before saving
        self.eway_bill_charges = 5.00
        self.godown_charges = 20.00
        
        # Ensure hamali_charges is at least 15.00
        if self.hamali_charges < 15.00:
            self.hamali_charges = 15.00

        # Set created_by and updated_by based on request user
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user

        # Call the superclass save method
        super(StandardRate, self).save(*args, **kwargs)

# New LR_Other_Charges model
class LR_Other_Charges(models.Model):
    id = models.AutoField(primary_key=True)
    charges_name = models.CharField(max_length=100)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='lr_other_charges_created_by', default=1
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lr_other_charges_updated_by'
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'lr_other_charges'

    def __str__(self):
        return self.charges_name

class LR_Bokking(models.Model):
    lr_no = models.AutoField(primary_key=True)
    branch = models.ForeignKey(
        BranchMaster, on_delete=models.SET_NULL, related_name='lr_bokking_branch', null=True)
    lr_number = models.CharField(max_length=10, unique=True, null=True, blank=True)
    date = models.DateField()
    coll_vehicle = models.ForeignKey(
        VehicalMaster, on_delete=models.SET_NULL, related_name='lr_bokking_coll_vehicle', null=True)
    tran_vehicle = models.ForeignKey(
        VehicalMaster, on_delete=models.SET_NULL, related_name='lr_bokking_tran_vehicle', null=True)
    del_vehicle = models.ForeignKey(
        VehicalMaster, on_delete=models.SET_NULL, related_name='lr_bokking_del_vehicle', null=True)
    remark = models.CharField(max_length=100,null=True,blank=True)
    from_branch = models.ForeignKey(
        BranchMaster, related_name='lr_bokking_from_branch', on_delete=models.SET_NULL, null=True)
    to_branch = models.ForeignKey(
        BranchMaster, related_name='lr_bokking_to_branch', on_delete=models.SET_NULL, null=True)
    consignor = models.ForeignKey(
        PartyMaster, related_name='lr_bokking_consignor_name', on_delete=models.SET_NULL, null=True)
    consignee = models.ForeignKey(
        PartyMaster, related_name='lr_bokking_consignee_name', on_delete=models.SET_NULL, null=True)
    pay_type = models.ForeignKey(
        PayTypes, related_name='lr_bokking_pay_type', on_delete=models.SET_NULL, null=True)
    billing_party = models.ForeignKey(
        PartyMaster, related_name='lr_bokking_billing_party', on_delete=models.SET_NULL, null=True)
    load_type = models.ForeignKey(
        LoadTypes, related_name='lr_load_type', on_delete=models.SET_NULL, null=True)
    type = models.ForeignKey(
        PaidTypes, related_name='lr_booking_type', on_delete=models.SET_NULL, null=True)
    coll_type = models.ForeignKey(
        CollectionTypes, related_name='lr_booking_collection_type', on_delete=models.SET_NULL, null=True)
    del_type = models.ForeignKey(
        DeliveryTypes, related_name='lr_booking_delivery_type', on_delete=models.SET_NULL, null=True)
    coll_at = models.ForeignKey(
        DestinationMaster, related_name='lr_booking_collection_at', on_delete=models.SET_NULL, null=True, blank=True)
    del_at = models.ForeignKey(
        DestinationMaster, related_name='lr_booking_delivery_at', on_delete=models.SET_NULL, null=True, blank=True)
    coll_km = models.FloatField(null=True, blank=True)  
    del_km = models.FloatField(null=True, blank=True)   


    descriptions = models.ManyToManyField(
        'LR_Bokking_Description', related_name='lr_bookings', blank=True)

    freight = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    e_way_bill_charges = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    collection = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    door_delivery = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    toll_escort_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    bilty_charges = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    hamali = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    godown_charges = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    insurance_charges = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
        # New fields referencing LR_Other_Charges
    other_charge_1 = models.ForeignKey(
        LR_Other_Charges, on_delete=models.SET_NULL, related_name='lr_bokking_other_charge_1', null=True, blank=True
    )
    other_charge_1_val = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    other_charge_2 = models.ForeignKey(
        LR_Other_Charges, on_delete=models.SET_NULL, related_name='lr_bokking_other_charge_2', null=True, blank=True
    )
    other_charge_2_val = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )    
    # waiting = models.DecimalField(
    #     max_digits=10, decimal_places=2, null=True, blank=True)
    fuel_surcharge = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    tchargedwt = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    tpackage = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    okpackage = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,default=0)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='lr_booking_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='lr_booking_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)
    printed_by_branch_manager = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'lr_bokking'

    def __str__(self):
        return f"{self.lr_no} - {self.remark}"


class LR_Bokking_Description(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.ForeignKey(
        ItemDetailsMaster, related_name='lr_booking_description_set', on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    actual_weight = models.DecimalField(max_digits=10, decimal_places=2)
    charged_weight = models.DecimalField(max_digits=10, decimal_places=2)
    unit_type = models.ForeignKey(
        QuotationTypes, related_name='lr_booking_unit_type_set', null=True, on_delete=models.SET_NULL)
    rate = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    # Changed challan_no and e_way_bill_no to CharField
    challan_no = models.CharField(max_length=50, validators=[RegexValidator(regex='^\d+$', message='Challan number must contain only digits.')])
    e_way_bill_no = models.CharField(max_length=50,null=True,blank=True)
    
    inv_value = models.IntegerField()

    class Meta:
        db_table = 'lr_bokking_description'

    def __str__(self):
        return f"{self.id} - {self.description}"

    def clean(self):
        # Validation for actual_weight and charged_weight
        if self.actual_weight < 50:
            raise ValidationError("Actual weight must be at least 50.")
        
        if self.charged_weight < 50:
            raise ValidationError("Charged weight must be at least 50.")
        
        if self.actual_weight > self.charged_weight:
            raise ValidationError("Actual weight cannot be greater than charged weight.")

        # Validation for inv_value
        if self.inv_value < 100:
            raise ValidationError("Invoice value must be at least 3 digits (e.g., 100 or higher).")

    def save(self, *args, **kwargs):
        # Call the clean method to perform validation
        self.clean()
        
        # Call the superclass save method
        super(LR_Bokking_Description, self).save(*args, **kwargs)