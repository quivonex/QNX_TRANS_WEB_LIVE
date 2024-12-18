from .models import PartyMaster, PartyTypes, BranchMaster
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django import forms
from django.contrib import admin
from .models import PartyTypes, PartyMaster
from branches.models import BranchMaster
from django.core.exceptions import PermissionDenied


@admin.register(PartyTypes)
class PartyTypesAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'created_by', 'is_active')
    search_fields = ('type_name',)
    list_filter = ('is_active',)
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user  # Update the updated_by field
        super().save_model(request, obj, form, change)


class PartyMasterForm(forms.ModelForm):
    class Meta:
        model = PartyMaster
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PartyMasterForm, self).__init__(*args, **kwargs)
        self.adjust_field_requirements()

    def adjust_field_requirements(self):
        """
        Adjust field requirements based on the party type.
        """
        # Ensure 'instance' is provided and has a 'party_type' attribute
        # ID '1' for 'Walking'
        if self.instance and hasattr(self.instance, 'party_type') and self.instance.party_type and self.instance.party_type.id == 1:
            # Make fields optional for 'Walking'
            self.fields['credit_period'].required = False
            self.fields['po_no'].required = False
            self.fields['vendor_code'].required = False
            self.fields['quotation_number'].required = False
        else:
            # Make fields required for other types
            self.fields['credit_period'].required = True
            self.fields['po_no'].required = True
            self.fields['vendor_code'].required = True
            self.fields['quotation_number'].required = True

    def clean(self):
        cleaned_data = super().clean()
        party_type = cleaned_data.get('party_type')

        # If "Walking" is selected, remove validation errors for optional fields
        if party_type and party_type.id == 1:
            # Remove validation errors for fields that are not required for "Walking"
            self.cleaned_data['credit_period'] = self.cleaned_data.get(
                'credit_period', None)
            self.cleaned_data['po_no'] = self.cleaned_data.get('po_no', None)
            self.cleaned_data['vendor_code'] = self.cleaned_data.get(
                'vendor_code', None)
            self.cleaned_data['quotation_number'] = self.cleaned_data.get(
                'quotation_number', None)

            # Clear any errors for these fields
            self._errors.pop('credit_period', None)
            self._errors.pop('po_no', None)
            self._errors.pop('vendor_code', None)
            self._errors.pop('quotation_number', None)
        # else:
        #     # Ensure required fields are filled for other types
        #     required_fields = ['credit_period', 'po_no',
        #                        'vendor_code', 'quotation_number']
        #     for field in required_fields:
        #         if not cleaned_data.get(field):
        #             self.add_error(field, 'This field is required.')

        return cleaned_data


@admin.register(PartyMaster)
class PartyMasterAdmin(admin.ModelAdmin):
    form = PartyMasterForm

    list_display = ('party_name', 'contact_no', 'email_id', 'address', 'pincode',
                    'branch', 'credit_period', 'area', 'po_no', 'vendor_code', 'is_active')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('party_name', 'contact_no', 'email_id',
                     'pincode', 'po_no', 'vendor_code')
    list_filter = ('is_active', 'branch', 'area')

    class Media:
        js = ('js/custom_party_master_view.js',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            user_profile = getattr(request.user, 'userprofile', None)
            if user_profile:
                return qs.filter(branch__in=user_profile.branches.all())
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "branch":
            if not request.user.is_superuser:
                user_profile = getattr(request.user, 'userprofile', None)
                if user_profile:
                    kwargs["queryset"] = BranchMaster.objects.filter(
                        id__in=user_profile.branches.values_list('id', flat=True))
        elif db_field.name == "area":
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            user_profile = getattr(request.user, 'userprofile', None)
            if user_profile:
                if not change:
                    if obj.branch not in user_profile.branches.all():
                        raise PermissionDenied(
                            "You cannot add parties to branches you do not have access to.")
                else:
                    if obj.branch not in user_profile.branches.all():
                        raise PermissionDenied(
                            "You cannot modify parties in other branches.")

        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user

        super().save_model(request, obj, form, change)
