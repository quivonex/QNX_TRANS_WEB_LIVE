from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class OwnerMaster(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False)
    contact_no = models.TextField(blank=False)
    email_id = models.TextField(blank=True)
    address = models.TextField(blank=True, null=True) 
    bank_name = models.CharField(max_length=255, blank=True)   
    IFSC_code = models.CharField(max_length=11, blank=True, validators=[
        RegexValidator(
            regex='^[A-Za-z]{4}[a-zA-Z0-9]{7}$',
            message='Invalid IFSC code format.'
        )
    ])
    account_no = models.CharField(max_length=20, blank=True)
    UPI_id = models.CharField(
        max_length=255, blank=True, null=True, validators=[EmailValidator])
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='owner_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owner_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'owner_master'
        verbose_name = 'Owner Master'
        verbose_name_plural = 'Owner Masters'

    def __str__(self):
        return self.name

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

        self.clean()

        # Set the updated_by field if updating an existing record
        if self.pk and request:
            self.updated_by = request.user
        # Set the created_by field if creating a new record
        elif request:
            self.created_by = request.user

        # Call the superclass save method
        super(OwnerMaster, self).save(*args, **kwargs)

class VehicalTypes(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=255, blank=False, unique=True)
    description = models.TextField(blank=True, null=True)
    capacity = models.IntegerField(validators=[MinValueValidator(1)], blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='vehical_type_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehical_type_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'vehical_types'
        verbose_name = 'Vehical Types'
        verbose_name_plural = 'Vehical Types'

    def __str__(self):
        return self.type_name

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
        super(VehicalTypes, self).save(*args, **kwargs)

class VendorTypes(models.Model):
    id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=255, blank=False, unique=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='vendor_type_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendor_type_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'vendor_types'
        verbose_name = 'Vendor Types'
        verbose_name_plural = 'Vendor Types'

    def __str__(self):
        return self.type_name

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
        super(VendorTypes, self).save(*args, **kwargs)

class VehicalMaster(models.Model):
    id = models.AutoField(primary_key=True)
    vehical_number = models.CharField(max_length=20, blank=False, unique=True, validators=[
        RegexValidator(
            regex='^[A-Z0-9-]+$',
            message='Vehical number must be alphanumeric and uppercase.'
        )
    ])
    vehical_type = models.ForeignKey(
        VehicalTypes, on_delete=models.CASCADE, related_name='vehicals')
    owner = models.ForeignKey(
        OwnerMaster, on_delete=models.CASCADE, related_name='vehicals')
    vendor_type = models.ForeignKey(
        VendorTypes, on_delete=models.CASCADE, related_name='vehicals', default=1)
    chassis_number = models.CharField(
        max_length=20, blank=False, default='DEFAULTCHASSIS123', validators=[
            RegexValidator(
                regex='^[A-Z0-9]+$',
                message='Chassis number must be alphanumeric and uppercase.'
            )
        ]
    )
    rc_book = models.ImageField(upload_to='RC_book/', blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='vehical_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehical_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'vehical_master'
        verbose_name = 'Vehical Master'
        verbose_name_plural = 'Vehical Masters'

    def __str__(self):
        return self.vehical_number

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
        super(VehicalMaster, self).save(*args, **kwargs)

class DriverMaster(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False)
    contact_no = models.TextField(blank=False)
    # email_id = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    license_no = models.CharField(max_length=20, blank=True, null=True, unique=True)
    license_exp_date = models.DateField(blank=True, null=True)
    aadhar_no = models.CharField(max_length=12, unique=True, blank=True,null = True, validators=[
        RegexValidator(
            regex='^\d{12}$',
            message='Aadhar number must be a 12-digit number.'
        )
    ])
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='driver_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='driver_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'driver_master'
        verbose_name = 'Driver Master'
        verbose_name_plural = 'Driver Masters'

    def __str__(self):
        return self.name

    def clean(self):
        # Custom validation for contact_no and email_id fields
        contact_numbers = self.contact_no.split(',')
        # email_addresses = self.email_id.split(',')

        # Validate each contact number (exactly 10 digits only)
        for number in contact_numbers:
            number = number.strip()  # Remove extra whitespace
            if number:
                # Check if the number is exactly 10 digits
                if not number.isdigit() or len(number) != 10:
                    raise ValidationError(f"Invalid contact number format: {number}. It must be exactly 10 digits.")

        # Validate each email address
        # for email in email_addresses:
        #     email = email.strip()  # Remove extra whitespace
        #     if email:
        #         try:
        #             validate_email(email)
        #         except ValidationError:
        #             raise ValidationError(f"Invalid email format: {email}")

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
        super(DriverMaster, self).save(*args, **kwargs)
