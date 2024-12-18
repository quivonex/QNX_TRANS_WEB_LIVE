import io
from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class CompanyMaster(models.Model):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=255, blank=False)
    company_logo = models.ImageField(
        upload_to='company_logos/', blank=True, null=True)
    slogan = models.CharField(max_length=255, blank=True, null=True)
    register_number = models.CharField(max_length=100, blank=False, unique=True, validators=[
        RegexValidator(
            regex='^[A-Z0-9]+$',
            message='Register number must be alphanumeric and uppercase.'
        )
    ])
    GST_number = models.CharField(max_length=15, blank=False, unique=True, validators=[
        RegexValidator(
            regex='^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}[Z]{1}[A-Z0-9]{1}$',
            message='Invalid GST number format.'
        )
    ])
    pan_no = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^[A-Z]{5}[0-9]{4}[A-Z]$', 'Invalid PAN format')],
    )
    INA_number = models.CharField(max_length=20, blank=False, unique=True)
    email_id = models.TextField(blank=False)
    contact_number = models.TextField(blank=False)
    address = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'company_master'
        verbose_name = 'Company Master'
        verbose_name_plural = 'Company Masters'

    def __str__(self):
        return self.company_name
    
    def clean(self):
        # Custom validation for contact_no and email_id fields
        contact_numbers = self.contact_number.split(',')
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
        request = kwargs.pop('request', None)

        # Convert company logo to WebP format
        self.company_logo = self.convert_image(self.company_logo)

        if self.pk:
            old_instance = CompanyMaster.objects.get(pk=self.pk)
            # Check for changes in the image field and delete the old file
            if old_instance.company_logo and old_instance.company_logo != self.company_logo:
                if default_storage.exists(old_instance.company_logo.path):
                    default_storage.delete(old_instance.company_logo.path)
            if request:
                self.updated_by = request.user
        else:
            if request:
                self.created_by = request.user

        self.clean()

        super(CompanyMaster, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._delete_files()
        super(CompanyMaster, self).delete(*args, **kwargs)

    def _delete_files(self):
        if self.company_logo and default_storage.exists(self.company_logo.path):
            default_storage.delete(self.company_logo.path)

    def convert_image(self, image_field):
        if image_field and image_field.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            # Open the uploaded image
            image = Image.open(image_field)
            # Convert image to WebP format
            output = io.BytesIO()
            image.save(output, format='WebP', quality=85)

            # Construct the new filename with .webp extension
            # Extract the filename with extension
            filename = image_field.name.split('/')[-1]
            # Replace extension with .webp
            new_filename = f"{filename.split('.')[0]}.webp"

            # Create a ContentFile with the converted image
            webp_image = ContentFile(output.getvalue(), new_filename)
            return webp_image
        return image_field


class FinancialYears(models.Model):
    id = models.AutoField(primary_key=True)
    year_name = models.CharField(max_length=9, blank=False, unique=True, validators=[
        RegexValidator(
            regex='^\d{4}-\d{2}$',
            message='Year name must be in the format YYYY-YY.'
        )
    ])
    start_date = models.DateField(blank=False)
    end_date = models.DateField(blank=False)
    description = models.TextField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='financial_years_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_years_updated_by')
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'financial_years'
        verbose_name = 'Financial Year'
        verbose_name_plural = 'Financial Years'

    def __str__(self):
        return self.year_name

    def save(self, *args, **kwargs):
        # Ensure end_date is after start_date
        if self.start_date >= self.end_date:
            raise ValueError("End date must be after start date")

        # Handle the is_current logic
        if self.is_current:
            # Set all other records to is_current = False
            FinancialYears.objects.filter(
                is_current=True).update(is_current=False)

        # Extract the request object from kwargs
        request = kwargs.pop('request', None)

        # Set the updated_by field if updating an existing record
        if self.pk and request:
            self.updated_by = request.user
        # Set the created_by field if creating a new record
        elif request:
            self.created_by = request.user

        # Call the superclass save method
        super(FinancialYears, self).save(*args, **kwargs)


class StateMaster(models.Model):
    id = models.AutoField(primary_key=True)
    state_name = models.CharField(max_length=100, blank=False, unique=True)
    state_code = models.CharField(max_length=10, blank=False, unique=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='state_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='state_updated_by', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'state_master'
        verbose_name = 'State Master'
        verbose_name_plural = 'State Masters'

    def __str__(self):
        return self.state_name

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
        super(StateMaster, self).save(*args, **kwargs)


class RegionMaster(models.Model):
    id = models.AutoField(primary_key=True)
    region_name = models.CharField(max_length=100, blank=False, unique=True)
    region_code = models.CharField(max_length=10, blank=True,null=True, unique=True, validators=[
        RegexValidator(
            regex='^[A-Z0-9]{3,10}$',
            message='Region code must be alphanumeric and between 3 to 10 characters long.'
        )
    ])
    state = models.ForeignKey(
        StateMaster, on_delete=models.CASCADE, related_name='regions')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_DEFAULT, related_name='region_created_by', default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='region_updated_by', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    flag = models.BooleanField(default=True)

    class Meta:
        db_table = 'region_master'
        verbose_name = 'Region Master'
        verbose_name_plural = 'Region Masters'

    def __str__(self):
        return self.region_name

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
        super(RegionMaster, self).save(*args, **kwargs)
