from django.contrib import admin
from .models import CompanyMaster, FinancialYears, StateMaster, RegionMaster


@admin.register(CompanyMaster)
class CompanyMasterAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'slogan', 'register_number', 'GST_number',
                    'INA_number', 'email_id', 'contact_number', 'is_active')
    search_fields = ('company_name', 'slogan', 'register_number',
                     'GST_number', 'INA_number', 'email_id')
    list_filter = ('is_active',)
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field
        super().save_model(request, obj, form, change)


@admin.register(FinancialYears)
class FinancialYearsAdmin(admin.ModelAdmin):
    list_display = ('year_name', 'start_date',
                    'end_date', 'is_current', 'is_active')
    search_fields = ('year_name',)
    list_filter = ('is_current', 'is_active')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field
        super().save_model(request, obj, form, change)


@admin.register(StateMaster)
class StateMasterAdmin(admin.ModelAdmin):
    list_display = ('state_name', 'state_code', 'is_active')
    search_fields = ('state_name', 'state_code')
    list_filter = ('is_active',)
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field
        super().save_model(request, obj, form, change)


@admin.register(RegionMaster)
class RegionMasterAdmin(admin.ModelAdmin):
    list_display = ('region_name', 'state', 'is_active')
    search_fields = ('region_name', 'region_code', 'state__state_name')
    list_filter = ('state', 'is_active')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field
        super().save_model(request, obj, form, change)
