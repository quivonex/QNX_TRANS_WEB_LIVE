from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from company.models import RegionMaster
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
User = get_user_model()

# Custom validator for the branch_weekly_off field
def validate_weekly_off_days(value):
    days = [day.strip() for day in value.split(',')]
    valid_days = {'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'}
    if any(day not in valid_days for day in days):
        raise ValidationError("Branch weekly off must contain valid days (e.g., 'MONDAY, TUESDAY').")

class BranchMaster(models.Model):
    id = models.AutoField(primary_key=True)
    branch_name = models.CharField(max_length=255, blank=False, unique=True)
    branch_code = models.CharField(max_length=20, blank=False, unique=True, validators=[
        RegexValidator(
            regex='^[A-Z0-9]+$',
            message='Branch code must be alphanumeric and uppercase.'
        )
    ])
    email_id = models.EmailField(
        max_length=255, blank=False, unique=True, validators=[EmailValidator])
    booking_contact = models.TextField(blank=False)
    delivery_contact = models.TextField(blank=False)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=False, validators=[
        RegexValidator(
            regex='^\\d{6}$',
            message='Pincode must be a 6-digit number.'
        )
    ])
    latitude = models.FloatField(
        blank=True, null=True, default=0.0,
        validators=[RegexValidator(
            regex='^-?([0-8]?[0-9]|90)\\.([0-9]{1,15})$',
            message='Latitude must be a valid float value between -90 and 90.'
        )]
    )
    longitude = models.FloatField(
        blank=True, null=True, default=0.0,
        validators=[RegexValidator(
            regex='^-?((1[0-7][0-9])|([0-9]{1,2}))\\.([0-9]{1,15})$',
            message='Longitude must be a valid float value between -180 and 180.'
        )]
    )
    region = models.ForeignKey(
        RegionMaster, on_delete=models.CASCADE, related_name='branches')
    branch_weekly_off = models.CharField(
        max_length=100, 
        blank=True, 
        validators=[validate_weekly_off_days],
        help_text="Enter valid days of the week (e.g., 'Monday, Tuesday')."
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='branch_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='branch_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'branch_master'
        verbose_name = 'Branch Master'
        verbose_name_plural = 'Branch Masters'

    def __str__(self):
        return self.branch_name or 'Unnamed Branch'
    
    def clean(self):
        # Custom validation for contact_no and email_id fields
        booking_contact = self.booking_contact.split(',')
        delivery_contact = self.delivery_contact.split(',')

        # Validate each contact number (exactly 10 digits only)
        for number in booking_contact:
            number = number.strip()  # Remove extra whitespace
            if number:
                # Check if the number is exactly 10 digits
                if not number.isdigit() or len(number) != 10:
                    raise ValidationError(f"Invalid contact number format: {number}. It must be exactly 10 digits.")

        # Validate each contact number (exactly 10 digits only)
        for number in delivery_contact:
            number = number.strip()  # Remove extra whitespace
            if number:
                # Check if the number is exactly 10 digits
                if not number.isdigit() or len(number) != 10:
                    raise ValidationError(f"Invalid contact number format: {number}. It must be exactly 10 digits.")


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
        self.clean()
        # Call the superclass save method
        super(BranchMaster, self).save(*args, **kwargs)


class EmployeeType(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='employee_type_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_type_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'employee_type'
        verbose_name = 'Employee Type'
        verbose_name_plural = 'Employee Types'

    def __str__(self):
        return self.type_name or 'Unnamed Type'

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
        super(EmployeeType, self).save(*args, **kwargs)


class EmployeeMaster(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False)
    contact_no = models.TextField(blank=False)
    email_id = models.TextField(blank=False)
    address = models.TextField(blank=True, null=True)
    employee_type = models.ForeignKey(
        EmployeeType, on_delete=models.CASCADE, related_name='employees')
    branch = models.ForeignKey(
        BranchMaster, on_delete=models.CASCADE, related_name='employees')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='employee_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'employee_master'
        verbose_name = 'Employee Master'
        verbose_name_plural = 'Employee Masters'

    def __str__(self):
        return self.name or 'Unnamed Employee'

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
        # Extract the request object from kwargs
        request = kwargs.pop('request', None)

        # Set the updated_by field if updating an existing record
        if self.pk and request:
            self.updated_by = request.user
        # Set the created_by field if creating a new record
        elif request:
            self.created_by = request.user
        self.clean()

        # Call the superclass save method
        super(EmployeeMaster, self).save(*args, **kwargs)
