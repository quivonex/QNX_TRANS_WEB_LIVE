from django.db import models,transaction
from django.contrib.auth import get_user_model
from branches.models import BranchMaster 
from parties.models import PartyMaster
from lr_booking.models import LR_Bokking
from vehicals.models import VehicalMaster,DriverMaster
from branches.models import EmployeeMaster
from collection.models import Collection,BookingMemo,TripMemo
from delivery.models import LocalMemoDelivery
from decimal import Decimal

User = get_user_model()

class GSTMaster(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)
    percentage = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='gst_master_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='gst_master_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'gst_master'
        verbose_name = 'GST Master'
        verbose_name_plural = 'GST Masters'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user
        super(GSTMaster, self).save(*args, **kwargs)

class PartyBilling(models.Model):
    id = models.AutoField(primary_key=True)
    branch_name = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, null=True, blank=True)
    bill_no = models.CharField(max_length=10, unique=True)
    date = models.DateField()
    bill_type = models.CharField(max_length=50, choices=[('PAID', 'PAID'), ('UNPAID', 'UNPAID')], default='UNPAID')
    billing_party = models.ForeignKey(
        PartyMaster, related_name='party_billing_billing_party', on_delete=models.SET_NULL, null=True)
    lr_booking = models.ManyToManyField(LR_Bokking, related_name='party_billing_lr_bookings', blank=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    gst = models.BooleanField(default=False)
    totla_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cgst = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default=1, related_name='party_billing_created_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'party_billing'

    def __str__(self):
        return f"{self.bill_no} - {self.date}"
        
class VoucherReceiptType(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)
    code = models.IntegerField(blank=True,null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='voucher_receipt_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='voucher_receipt_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'voucher_receipt_type'
        verbose_name = 'voucher Receipt'
        verbose_name_plural = 'voucher Receipts'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user
        super(VoucherReceiptType, self).save(*args, **kwargs)

class VoucherReceiptBranch(models.Model):
    id = models.AutoField(primary_key=True)       
    date = models.DateField()
    branch_name = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, null=True, blank=True)     
    receipt_type = models.ForeignKey(
        VoucherReceiptType, related_name='voucher_receipt_branch_receipt_type', on_delete=models.SET_NULL, null=True)
    lr_booking = models.ManyToManyField(LR_Bokking, related_name='voucher_receipt_branch_lr_bookings', blank=True)
    party_billing = models.ManyToManyField(PartyBilling, related_name='voucher_receipt_branch_party_billing', blank=True)
    to_branch = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, null=True, blank=True,related_name='to_branch_to_send_money')
    to_branch_amt = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    totla_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default=1, related_name='voucher_receipt_branch_created_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'voucher_receipt_branch'

    def __str__(self):
        return f"{self.bill_no} - {self.date}"        

class MoneyReceipt(models.Model):
    id = models.AutoField(primary_key=True)       
    date = models.DateField()
    branch_name = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, null=True, blank=True)     
    receipt_type = models.ForeignKey(
        VoucherReceiptType, related_name='money_receipth_receipt_type', on_delete=models.SET_NULL, null=True)
    pay_type = models.CharField(max_length=50, choices=[('UPI', 'UPI'), ('RTGS/NFT', 'RTGS/NFT'),('CHECK', 'CHECK')], default='UPI')
    lr_booking = models.ManyToManyField(LR_Bokking, related_name='money_receipt_lr_bookings', blank=True)
    party_billing = models.ManyToManyField(PartyBilling, related_name='money_receipt_party_billing', blank=True)
    utr_no = models.CharField(max_length=100, blank=True, null=True)
    rtgs_no = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    check_no = models.CharField(max_length=100, blank=True, null=True)
    check_date = models.DateField(blank=True, null=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    total_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default=1, related_name='money_receipt_created_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'money_receipt'

    def __str__(self):
        return f"{self.bill_no} - {self.date}"

class VoucherPaymentType(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)
    effect = models.CharField(
        max_length=255, null=True, blank=False)
    mode_type = models.CharField(max_length=50, choices=[('SINGLE', 'SINGLE'), ('MULTIPLE', 'MULTIPLE')], default='SINGLE')
    code = models.IntegerField(blank=True,null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='voucher_payment_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='voucher_payment_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'voucher_payment_type'
        verbose_name = 'payment Receipt'
        verbose_name_plural = 'payment Receipts'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user
        super(VoucherPaymentType, self).save(*args, **kwargs)

class VoucherPaymentBranch(models.Model):
    id = models.AutoField(primary_key=True)       
    date = models.DateField()
    branch_name = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, null=True, blank=True)     
    voucher_no = models.CharField(max_length=10, unique=True)
    pay_type = models.ForeignKey(VoucherPaymentType, on_delete=models.SET_NULL, null=True, blank=True)
    vehical_no = models.ForeignKey(VehicalMaster, on_delete=models.SET_NULL, null=True, blank=True)
    lr_no = models.ForeignKey(LR_Bokking, on_delete=models.SET_NULL, null=True, blank=True)
    employee = models.ForeignKey(EmployeeMaster, on_delete=models.SET_NULL, null=True, blank=True)
    party = models.ForeignKey(PartyMaster, on_delete=models.SET_NULL, null=True, blank=True)
    lcm_no = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, blank=True)
    booking_memo = models.ForeignKey(BookingMemo, on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey(DriverMaster, on_delete=models.SET_NULL, null=True, blank=True)
    ldm_no = models.ForeignKey(LocalMemoDelivery, on_delete=models.SET_NULL, null=True, blank=True)
    trip_no = models.ForeignKey(TripMemo, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default=1, related_name='voucher_payment_branch_created_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'voucher_payment'

    def __str__(self):
        return f"{self.bill_no} - {self.date}"

class CashBook(models.Model):
    id = models.AutoField(primary_key=True)           
    branch_name = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, null=True, blank=True) 
    date = models.DateField()
    opening_balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)        
    credit = models.ManyToManyField(VoucherReceiptBranch, related_name='cash_book_credit_side', blank=True)
    debit = models.ManyToManyField(VoucherPaymentBranch, related_name='cash_book_debit_side', blank=True)    
    closing_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        db_table = 'cash_book'

    def __str__(self):
        return f"{self.bill_no} - {self.date}" 

    @transaction.atomic
    def credit_operation(self, branch_id, voucher_id, date, amount):
        """
        Perform credit operations on the CashBook model.

        Parameters:
        - branch_id: ID of the BranchMaster
        - voucher_id: ID of the VoucherReceiptBranch to be added to credit
        - date: The date for the operation
        - amount: The credit amount to be added
        """
        # Check if a record exists for the branch and date
        cash_book = CashBook.objects.filter(branch_name_id=branch_id, date=date).first()
        amount = Decimal(amount)
        
        if cash_book:
            # Record exists, add the voucher to credit and update the closing balance
            voucher = VoucherReceiptBranch.objects.get(id=voucher_id)
            cash_book.credit.add(voucher)
            cash_book.closing_balance += amount
            cash_book.save()
        else:
            # Check for the latest record before the given date for the branch
            last_record = CashBook.objects.filter(branch_name_id=branch_id, date__lt=date).order_by('-date').first()
            
            if last_record:
                # Create a new record using the last record's closing balance as opening balance
                opening_balance = last_record.closing_balance
            else:
                # No previous record, opening balance is 0
                opening_balance = Decimal('0.00')
            
            # Create a new CashBook record
            cash_book = CashBook.objects.create(
                branch_name_id=branch_id,
                date=date,
                opening_balance=opening_balance,
                closing_balance=opening_balance + amount
            )
            voucher = VoucherReceiptBranch.objects.get(id=voucher_id)
            cash_book.credit.add(voucher)
            cash_book.save()

        return cash_book 
    @transaction.atomic
    def debit_operation(self, branch_id, payment_id, date, amount):
        """
        Perform debit operations on the CashBook model.

        Parameters:
        - branch_id: ID of the BranchMaster
        - payment_id: ID of the VoucherPaymentBranch to be added to debit
        - date: The date for the operation
        - amount: The debit amount to be subtracted
        """
        # Check if a record exists for the branch and date
        cash_book = CashBook.objects.filter(branch_name_id=branch_id, date=date).first()
        amount = Decimal(amount)
        
        if cash_book:
            # Record exists, add the payment to debit and update the closing balance
            payment = VoucherPaymentBranch.objects.get(id=payment_id)
            cash_book.debit.add(payment)
            cash_book.closing_balance -= amount
            cash_book.save()
        else:
            # Check for the latest record before the given date for the branch
            last_record = CashBook.objects.filter(branch_name_id=branch_id, date__lt=date).order_by('-date').first()
            
            if last_record:
                # Create a new record using the last record's closing balance as opening balance
                opening_balance = last_record.closing_balance
            else:
                # No previous record, opening balance is 0
                opening_balance = Decimal('0.00')
            
            # Create a new CashBook record
            cash_book = CashBook.objects.create(
                branch_name_id=branch_id,
                date=date,
                opening_balance=opening_balance,
                closing_balance=opening_balance - amount
            )
            payment = VoucherPaymentBranch.objects.get(id=payment_id)
            cash_book.debit.add(payment)
            cash_book.save()

        return cash_book      

class BillingSubmission(models.Model):
    id = models.AutoField(primary_key=True)               
    branch_name = models.ForeignKey(BranchMaster, on_delete=models.SET_NULL, null=True, blank=True)
    sub_no = models.CharField(max_length=10, unique=True) 
    date = models.DateField()       
    bill_no = models.ForeignKey(PartyBilling, on_delete=models.SET_NULL, null=True, blank=True)
    sub_by = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default=1, related_name='billing_submission_branch_created_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'billing_submission'

    def __str__(self):
        return f"{self.bill_no} - {self.date}"        

class DeductionReasonType(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(
        max_length=255, unique=True, blank=False)    
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='deduction_reason_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='deduction_reason_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'deduction_reason_type'
        verbose_name = 'Deduction Reason'
        verbose_name_plural = 'Deduction Reasons'

    def __str__(self):
        return self.type_name or 'Unnamed type'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        if self.pk and request:
            self.updated_by = request.user
        elif request:
            self.created_by = request.user
        super(DeductionReasonType, self).save(*args, **kwargs)

class Deduction(models.Model):
    id = models.AutoField(primary_key=True)           
    lr_booking = models.ForeignKey(LR_Bokking, on_delete=models.SET_NULL, null=True, blank=True)
    party_billing = models.ForeignKey(PartyBilling, on_delete=models.SET_NULL, null=True, blank=True)    
    deduct_amt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reason = models.ForeignKey(DeductionReasonType, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, default=1, related_name='deduction_created_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'deduction'

    def __str__(self):
        return f"{self.bill_no} - {self.date}"        
