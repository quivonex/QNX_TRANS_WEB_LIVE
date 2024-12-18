from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from branches.models import BranchMaster
from destinations.models import DestinationMaster
from django.contrib.auth import get_user_model
from transactions.models import  PayTypes
User = get_user_model()

# Custom validator for the branch_weekly_off field
def validate_weekly_off_days(value):
    days = [day.strip() for day in value.split(',')]
    valid_days = {'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'}
    if any(day not in valid_days for day in days):
        raise ValidationError("Branch weekly off must contain valid days (e.g., 'Monday, Tuesday').")

class PartyTypes(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='party_type_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='party_type_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'party_types'
        verbose_name = 'Party Type'
        verbose_name_plural = 'Party Types'

    def __str__(self):
        return self.type_name or 'Unnamed Party Type'

    def save(self, *args, **kwargs):
        # Extract the request object from kwargs
        request = kwargs.pop('request', None)

        # Set the updated_by field if updating an existing record
        if self.pk and request:
            self.updated_by = request.user
        # Set the created_by field if creating a new record
        elif request:
            self.created_by = request.user

        # Call the superclass save method
        super(PartyTypes, self).save(*args, **kwargs)


class PartyMaster(models.Model):
    id = models.AutoField(primary_key=True)
    party_type = models.ForeignKey(        
        PartyTypes, on_delete=models.SET_NULL, null=True, related_name='parties')
    pay_type = models.ForeignKey(
        PayTypes, related_name='party_master_pay_type', on_delete=models.SET_NULL, null=True)
    party_name = models.CharField(max_length=255, blank=False)
    address = models.TextField(blank=True, null=True)
    area = models.ForeignKey(
        DestinationMaster, on_delete=models.CASCADE, related_name='parties')

    contact_no = models.TextField(blank=False)
    email_id = models.TextField(blank=False)
    gst_no = models.CharField(
        max_length=15,
        blank=True
        # ,validators=[
        #     RegexValidator(
        #         regex='^[0-9A-Z]{15}$',
        #         message='GST number must be a 15-character alphanumeric string.'
        #     )
        # ]
    )

    pincode = models.CharField(max_length=10, blank=False, validators=[
        RegexValidator(
            regex='^\\d{6}$',
            message='Pincode must be a 6-digit number.'
        )
    ])
    branch = models.ForeignKey(
        BranchMaster, on_delete=models.CASCADE, related_name='parties')
    credit_period = models.PositiveIntegerField(
        blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(365)])
    credit_amount = models.PositiveIntegerField(blank=True, null=True)

    po_no = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        validators=[RegexValidator(
            regex='^\d+$', message='PO number must contain only digits.')]
    )
    vendor_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex='^\d+$', message='Vendor code must contain only digits.')]
    )
    quotation_number = models.CharField(
        max_length=50, null=True, blank=True)  # New field for quotation number
    party_weekly_off = models.CharField(
        max_length=100, 
        blank=True, 
        validators=[validate_weekly_off_days],
        help_text="Enter valid days of the week (e.g., 'Monday, Tuesday')."
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='party_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='party_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'party_master'
        verbose_name = 'Party Master'
        verbose_name_plural = 'Party Masters'

    def __str__(self):
        return self.party_name or 'Unnamed Party'

    def clean(self):
        # Custom validation for contact_no and email_id fields
        contact_numbers = self.contact_no.split(',')
        email_addresses = self.email_id.split(',')

        # Validate each contact number (exactly 10 digits only)
        for number in contact_numbers:
            number = number.strip()  # Remove extra whitespace
            if number:
                # Check if the number is exactly 10 digits
                if not number.isdigit() or len(number) != 10:
                    raise ValidationError(f"Invalid contact number format: {number}. It must be exactly 10 digits.")

        # Validate each email address
        for email in email_addresses:
            email = email.strip()  # Remove extra whitespace
            if email:
                try:
                    validate_email(email)
                except ValidationError:
                    raise ValidationError(f"Invalid email format: {email}")

    def save(self, *args, **kwargs):
        # Ensure pincode is numeric and 6 digits
        if not self.pincode.isdigit() or len(self.pincode) != 6:
            raise ValueError("Pincode must be a 6-digit number")

        # Extract the request object from kwargs
        request = kwargs.pop('request', None)

        # Set the updated_by field if updating an existing record
        if self.pk and request:
            self.updated_by = request.user
        # Set the created_by field if creating a new record
        elif request:
            self.created_by = request.user

        # Call the clean method to validate contact_no and email_id fields
        self.clean()

        # Call the superclass save method
        super(PartyMaster, self).save(*args, **kwargs)