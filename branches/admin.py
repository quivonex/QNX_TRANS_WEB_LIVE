from branches.models import BranchMaster
from .models import EmployeeMaster
from django.contrib import admin
from .models import BranchMaster, EmployeeType, EmployeeMaster

from django.core.exceptions import PermissionDenied


@admin.register(BranchMaster)
class BranchMasterAdmin(admin.ModelAdmin):
    list_display = ('branch_name', 'branch_code', 'email_id', 'booking_contact',
                    'delivery_contact', 'address', 'pincode', 'region', 'is_active')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('branch_name', 'branch_code', 'email_id', 'pincode')
    list_filter = ('is_active', 'region')

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field
        super().save_model(request, obj, form, change)


@admin.register(EmployeeType)
class EmployeeTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'description',
                    'is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('type_name',)
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field
        super().save_model(request, obj, form, change)


# # @admin.register(EmployeeMaster)
# class EmployeeMasterAdmin(admin.ModelAdmin):
#     list_display = ('name', 'contact_no', 'email_id',
#                     'employee_type', 'branch', 'is_active')
#     readonly_fields = ('created_at', 'updated_at')
#     search_fields = ('name', 'contact_no', 'email_id')
#     list_filter = ('is_active', 'employee_type', 'branch')

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.is_staff:
#             user_profile = getattr(request.user, 'userprofile', None)
#             if user_profile and user_profile.branch:
#                 return qs.filter(branch=user_profile.branch)
#         return qs

#     def save_model(self, request, obj, form, change):
#         if not change:
#             user_profile = getattr(request.user, 'userprofile', None)
#             if user_profile and user_profile.branch:
#                 obj.branch = user_profile.branch
#         elif obj.branch != getattr(request.user.userprofile, 'branch', None):
#             raise PermissionDenied(
#                 "You cannot modify employees in other branches.")
#         super().save_model(request, obj, form, change)


# admin.site.register(EmployeeMaster, EmployeeMasterAdmin)


class EmployeeMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_no', 'email_id',
                    'employee_type', 'branch', 'is_active')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('name', 'contact_no', 'email_id')
    list_filter = ('is_active', 'employee_type', 'branch')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            user_profile = getattr(request.user, 'userprofile', None)
            if user_profile:
                # Filter employees based on branches the user has access to
                return qs.filter(branch__in=user_profile.branches.all())
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "branch":
            if not request.user.is_superuser:
                user_profile = getattr(request.user, 'userprofile', None)
                if user_profile:
                    # Limit branch choices to those the user has access to
                    kwargs["queryset"] = BranchMaster.objects.filter(
                        id__in=user_profile.branches.values_list('id', flat=True))
            # Superusers can select any branch
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            user_profile = getattr(request.user, 'userprofile', None)
            if user_profile:
                if not change:  # New record
                    # Ensure the branch is one the user has access to
                    if obj.branch not in user_profile.branches.all():
                        raise PermissionDenied(
                            "You cannot add employees to branches you do not have access to.")
                else:  # Existing record
                    # Ensure the branch is one the user has access to
                    if obj.branch not in user_profile.branches.all():
                        raise PermissionDenied(
                            "You cannot modify employees in other branches.")

        # Set created_by and updated_by fields
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field

        # Superusers have no restriction
        super().save_model(request, obj, form, change)


admin.site.register(EmployeeMaster, EmployeeMasterAdmin)
