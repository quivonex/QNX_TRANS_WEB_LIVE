from django.contrib import admin
from .models import OwnerMaster, VendorTypes, VehicalTypes, VehicalMaster, DriverMaster


@admin.register(OwnerMaster)
class OwnerMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_no', 'email_id', 
                    'IFSC_code', 'account_no', 'UPI_id', 'is_active')
    search_fields = ('name', 'contact_no', 'email_id')
    list_filter = ('is_active',)
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field
        super().save_model(request, obj, form, change)


@admin.register(VendorTypes)
class VendorTypesAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'created_at', 'is_active')
    search_fields = ('type_name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field
        super().save_model(request, obj, form, change)


@admin.register(VehicalTypes)
class VehicalTypesAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'description', 'is_active')
    search_fields = ('type_name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field
        super().save_model(request, obj, form, change)


@admin.register(VehicalMaster)
class VehicalMasterAdmin(admin.ModelAdmin):
    list_display = ('vehical_number', 'vehical_type',
                    'owner', 'vendor_type', 'is_active')
    search_fields = ('vehical_number',)
    list_filter = ('is_active', 'vehical_type', 'owner')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field
        super().save_model(request, obj, form, change)


@admin.register(DriverMaster)
class DriverMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_no', 
                    'license_no', 'license_exp_date', 'is_active')
    search_fields = ('name', 'contact_no', 'email_id', 'license_no')
    list_filter = ('is_active',)
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field
        super().save_model(request, obj, form, change)
