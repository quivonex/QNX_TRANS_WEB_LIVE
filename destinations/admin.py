# from django.contrib import admin
# from .models import DestinationMaster
# from branches.models import BranchMaster
# from django.core.exceptions import PermissionDenied


# class DestinationMasterAdmin(admin.ModelAdmin):
#     list_display = ('destination_name', 'branch',
#                     'pin_code', 'kilometer', 'is_active')
#     readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
#     search_fields = ('destination_name', 'pin_code')
#     list_filter = ('is_active', 'branch')

#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if not request.user.is_superuser:
#             user_profile = getattr(request.user, 'userprofile', None)
#             if user_profile:
#                 # Filter destinations based on branches the user has access to
#                 return qs.filter(branch__in=user_profile.branches.all())
#         return qs

#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "branch":
#             if not request.user.is_superuser:
#                 user_profile = getattr(request.user, 'userprofile', None)
#                 if user_profile:
#                     # Limit branch choices to those the user has access to
#                     kwargs["queryset"] = BranchMaster.objects.filter(
#                         id__in=user_profile.branches.values_list('id', flat=True))
#             # Superusers can select any branch
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)

#     def save_model(self, request, obj, form, change):
#         if not request.user.is_superuser:
#             user_profile = getattr(request.user, 'userprofile', None)
#             if user_profile:
#                 if not change:  # New record
#                     # Ensure the branch is one the user has access to
#                     if obj.branch not in user_profile.branches.all():
#                         raise PermissionDenied(
#                             "You cannot add destinations to branches you do not have access to.")
#                 else:  # Existing record
#                     # Ensure the branch is one the user has access to
#                     if obj.branch not in user_profile.branches.all():
#                         raise PermissionDenied(
#                             "You cannot modify destinations in other branches.")
#         # Set created_by and updated_by fields
#         if not change:  # Creating a new record
#             obj.created_by = request.user
#         obj.updated_by = request.user  # Update the updated_by field

#         # Superusers have no restriction
#         super().save_model(request, obj, form, change)


# admin.site.register(DestinationMaster, DestinationMasterAdmin)


# # admin.py
# from django import forms
# from django.contrib import admin
# from .models import DestinationMaster
# from branches.models import BranchMaster


# class DestinationMasterForm(forms.ModelForm):
#     branch_pincode = forms.CharField(
#         widget=forms.HiddenInput(), required=False)
#     pin_code = forms.CharField(required=True)  # Make it visible for testing

#     class Meta:
#         model = DestinationMaster
#         fields = '__all__'
#         widgets = {
#             'kilometer': forms.NumberInput(attrs={'readonly': 'readonly'}),
#         }

#     class Media:
#         js = ('admin/js/refresh_kilometer.js',)


# class DestinationMasterAdmin(admin.ModelAdmin):
#     form = DestinationMasterForm
#     list_display = ('destination_name', 'branch',
#                     'pin_code', 'kilometer', 'is_active')
#     readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
#     search_fields = ('destination_name', 'pin_code')
#     list_filter = ('is_active', 'branch')

#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         if obj:
#             branch_pincode = obj.branch.pincode if obj.branch else ''
#             form.base_fields['branch_pincode'].initial = branch_pincode
#             form.base_fields['pin_code'].initial = obj.pin_code

#             print("Initializing form with pin_code:", obj.pin_code)
#         return form


# admin.site.register(DestinationMaster, DestinationMasterAdmin)


# admin.py
from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from .models import DestinationMaster
from branches.models import BranchMaster


class DestinationMasterForm(forms.ModelForm):
    branch_pincode = forms.CharField(
        widget=forms.HiddenInput(), required=False)
    pin_code = forms.CharField(required=True)  # Make it visible for testing

    class Meta:
        model = DestinationMaster
        fields = '__all__'
        widgets = {
            'kilometer': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }

    class Media:
        js = ('admin/js/refresh_kilometer.js',)


class DestinationMasterAdmin(admin.ModelAdmin):
    form = DestinationMasterForm
    list_display = ('destination_name', 'branch',
                    'pin_code', 'kilometer', 'is_active')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('destination_name', 'pin_code')
    list_filter = ('is_active', 'branch')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            user_profile = getattr(request.user, 'userprofile', None)
            if user_profile:
                # Filter destinations based on branches the user has access to
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
                            "You cannot add destinations to branches you do not have access to.")
                else:  # Existing record
                    # Ensure the branch is one the user has access to
                    if obj.branch not in user_profile.branches.all():
                        raise PermissionDenied(
                            "You cannot modify destinations in other branches.")
        # Set created_by and updated_by fields
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field

        # Superusers have no restriction
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            branch_pincode = obj.branch.pincode if obj.branch else ''
            form.base_fields['branch_pincode'].initial = branch_pincode
            form.base_fields['pin_code'].initial = obj.pin_code

            print("Initializing form with pin_code:", obj.pin_code)
        return form


admin.site.register(DestinationMaster, DestinationMasterAdmin)
