import json
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from django.contrib import admin


from .models import StandardRate, LR_Bokking, BranchMaster, ItemDetailsMaster, QuotationTypes, LR_Bokking_Description
from django.contrib.auth import get_user_model
from django.contrib.admin.helpers import AdminForm
User = get_user_model()


# class StandardRateAdmin(admin.ModelAdmin):
#     list_display = ('id', 'quotation_date', 'from_branch', 'to_branch',
#                     'rate', 'expiry_date')
#     search_fields = ('from_branch__branch_name', 'to_branch__branch_name',
#                      'type__name', 'measurement__name')
#     list_filter = ('quotation_date', 'expiry_date', 'from_branch',
#                    'to_branch')
#     ordering = ('-quotation_date',)
#     readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

#     def save_model(self, request, obj, form, change):
#         # Set the created_by and updated_by fields
#         if not change:  # Creating a new record
#             obj.created_by = request.user
#         obj.updated_by = request.user
#         super().save_model(request, obj, form, change)


# admin.site.register(StandardRate, StandardRateAdmin)

@admin.register(StandardRate)
class StandardRateAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Standard Rate', {
            'fields': (('quotation_date'), ('diesel_rate', 'approve_date', 'expiry_date')),
            'classes': ('wide',),
        }),
        ('Branch Details', {
            'fields': (('from_branch', 'to_branch'), ('type', 'measurement')),
            'classes': ('wide',),
        }),
        ('Charges', {
            'fields': (('up', 'to'), ('rate', 'coll_charges', 'del_charges', 'hamali_charges', 'godown_charges')),
            'classes': ('wide',),
        }),
        ('Additional Charges', {
            'fields': ((), ('insurance_charges')),
            'classes': ('wide',),
        }),
        ('Eway and Insurance', {
            'fields': (('eway_bill_charges'),),
            'classes': ('wide',),
        }),
        # ('Timestamps', {
        #     'fields': (('created_at', 'updated_at'), ('updated_by',)),
        #     'classes': ('wide',),
        # }),
    )


# class LR_BokkingAdmin(admin.ModelAdmin):
#     list_display = (
#         'lr_no', 'branch', 'date', 'coll_vehicle', 'from_branch', 'to_branch',)
#     list_filter = (
#         'branch', 'date', 'from_branch', 'to_branch', 'pay_type',
#         'load_type', 'type', 'coll_type', 'del_type', 'is_active'
#     )
#     search_fields = ('lr_no', 'challan_no', 'e_way_bill_no',
#                      'consignor__name', 'consignee__name')
#     readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

#     def save_model(self, request, obj, form, change):
#         # Set the created_by and updated_by fields
#         if not change:  # Creating a new record
#             obj.created_by = request.user
#         obj.updated_by = request.user
#         super().save_model(request, obj, form, change)


# admin.site.register(LR_Bokking, LR_BokkingAdmin)


# @admin.register(LR_Bokking)
# class LRBookingAdmin(admin.ModelAdmin):
#     list_display = (
#         'lr_no', 'branch', 'date', 'coll_vehicle', 'from_branch', 'to_branch',)
#     list_filter = (
#         'branch', 'date', 'is_active'
#     )
#     search_fields = ('lr_no', 'challan_no', 'e_way_bill_no',
#                      'consignor__name', 'consignee__name')
#     readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')

#     # Add a custom button to access the custom view
#     change_list_template = "admin/lr_booking_change_list.html"

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('custom-admin-view/', self.admin_site.admin_view(self.custom_view),
#                  name='custom_admin_view'),
#         ]
#         return custom_urls + urls

#     def custom_view(self, request):
#         # Fetch all LR Booking records
#         lr_bokkings = LR_Bokking.objects.all()
#         # Render the custom admin template with context data
#         return render(request, 'admin/custom_admin_view.html', {'lr_bokkings': lr_bokkings})


class LRBookingForm(forms.ModelForm):
    class Meta:
        model = LR_Bokking
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:  # Existing record
            self.fields['descriptions'].queryset = LR_Bokking_Description.objects.filter(
                lr_bookings=self.instance)
        else:  # New record
            self.fields['descriptions'].queryset = LR_Bokking_Description.objects.none()


@admin.register(LR_Bokking)
class LRBookingAdmin(admin.ModelAdmin):
    # form = LRBookingForm
    list_display = (
        'lr_no', 'branch', 'date', 'coll_vehicle', 'from_branch', 'to_branch',
    )
    list_filter = (
        'branch', 'date', 'is_active'
    )
    search_fields = (
        'lr_no', 'challan_no', 'e_way_bill_no', 'consignor_name', 'consignee__name'
    )
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    change_form_template = "admin/custom_lr_booking_view.html"

    def get_changeform_initial_data(self, request):
        extra_field_value = 'Your Extra Field Value'
        return {
            'lrbookings': LR_Bokking.objects.all(),
            'branches': BranchMaster.objects.all(),
            'description': ItemDetailsMaster.objects.all(),
            'extra_field_value': extra_field_value,
            'unit_type': QuotationTypes.objects.all()
        }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        fields_to_modify = ['branch', 'coll_vehicle', 'tran_vehicle', 'del_vehicle', 'from_branch', 'to_branch', 'consignor', 'consignee',
                            'pay_type', 'billing_party', 'load_type', 'type', 'coll_type', 'del_type', 'coll_at', 'del_at', 'unit_type', 'rate']

        for field_name in fields_to_modify:
            if field_name in form.base_fields:
                field = form.base_fields[field_name]
                field.widget.can_add_related = False
                field.widget.can_change_related = False
                field.widget.can_delete_related = False
                field.widget.can_view_related = False

        return form

    def add_view(self, request, form_url='', extra_context=None):
        if request.method == 'POST':
            form = self.get_form(request)(request.POST)
            if form.is_valid():
                new_object = form.save(commit=False)
                serialized_table_data = request.POST.get(
                    'serialized_table_data')
                if serialized_table_data:
                    table_data = json.loads(serialized_table_data)

                    descriptions_to_add = []
                    for item in table_data:
                        if item.get('id') == '0':
                            new_description = LR_Bokking_Description.objects.create(
                                description=ItemDetailsMaster.objects.get(
                                    pk=item['description']) if item.get('description') else None,
                                quantity=item.get('quantity', 0),
                                actual_weight=item.get('actual_weight', 0),
                                charged_weight=item.get(
                                        'charged_weight', 0),
                                unit_type=QuotationTypes.objects.get(
                                        pk=item['unit_type']) if item.get('unit_type') else None,
                                rate=item.get('rate', 0),
                                challan_no=item.get('challan_no', 0),
                                inv_value=item.get('inv_value', 0),
                                e_way_bill_no=item.get('e_way_bill_no', 0)
                            )
                            descriptions_to_add.append(new_description)
                        else:
                            existing_description = LR_Bokking_Description.objects.get(
                                pk=item['id'])
                            descriptions_to_add.append(existing_description)

                    new_object.save()  # Save the main object
                    new_object.descriptions.set(
                        descriptions_to_add)  # Associate descriptions

                # Redirect to the change view of the newly created object
                return redirect(f'/admin/{self.model._meta.app_label}/{self.model._meta.model_name}/{new_object.pk}/change/')
        else:
            form = self.get_form(request)()

        admin_form = AdminForm(form, self.get_fieldsets(
            request), self.prepopulated_fields)

        extra_context = extra_context or {}
        context_data = self.get_changeform_initial_data(request)
        extra_context.update(context_data)
        extra_context.update({
            'form': form,
            'adminform': admin_form,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
            'save_as': self.save_as,
            'is_popup': request.GET.get('_popup', False),
            'to_field': request.GET.get('_to_field', ''),
            'media': self.media,
            'change': False,  # Indicates that this is an add view
        })
        # return render(request, "admin/custom_lr_booking_view.html", extra_context)
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)

        if request.method == 'POST':
            form = self.get_form(request, obj=obj)(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                cleaned_data = form.cleaned_data
                branch_value = cleaned_data.get('branch')
                descriptions_value = cleaned_data.get(
                    'descriptions')
                date = cleaned_data.get('date')

                print(f"Branch: {date}")
            else:
                cleaned_data = form.cleaned_data
                branch_value = cleaned_data.get('branch')
                descriptions_value = cleaned_data.get(
                    'descriptions')
                date = cleaned_data.get('date')

                print(f"Branch: {date}")
                print(f"descriptions: {descriptions_value}")
                print("================================")
                print("Form is not valid.")
                # Check if 'serialized_table_data' is present and not empty
            serialized_table_data = request.POST.get(
                'serialized_table_data', '')

            if serialized_table_data:
                try:
                    table_data = json.loads(serialized_table_data)
                    descriptions_to_add = []
                    descriptions_to_update = []

                    for item in table_data:

                        if item.get('id') == '0':  # New record
                            new_description = LR_Bokking_Description.objects.create(
                                description=ItemDetailsMaster.objects.get(
                                    pk=item['description']) if item.get('description') else None,
                                quantity=item.get('quantity', 0),
                                actual_weight=item.get('actual_weight', 0),
                                charged_weight=item.get('charged_weight', 0),
                                unit_type=QuotationTypes.objects.get(
                                    pk=item['unit_type']) if item.get('unit_type') else None,
                                # Directly using the rate value
                                rate=item.get('rate', 0),
                                challan_no=item.get('challan_no', 0),
                                inv_value=item.get('inv_value', 0),
                                e_way_bill_no=item.get('e_way_bill_no', 0)
                            )
                            descriptions_to_add.append(new_description)
                        else:  # Existing record
                            # Fetch the existing LR_Bokking_Description object by ID
                            existing_description = LR_Bokking_Description.objects.get(
                                pk=item['id'])
                            existing_description.description = ItemDetailsMaster.objects.get(
                                pk=item['description']) if item.get('description') else None
                            existing_description.quantity = item.get(
                                'quantity', 0)
                            existing_description.actual_weight = item.get(
                                'actual_weight', 0)
                            existing_description.charged_weight = item.get(
                                'charged_weight', 0)
                            existing_description.unit_type = QuotationTypes.objects.get(
                                pk=item['unit_type']) if item.get('unit_type') else None
                            existing_description.rate = item.get('rate', 0)
                            existing_description.challan_no = item.get(
                                'challan_no', 0)
                            existing_description.inv_value = item.get(
                                'inv_value', 0)
                            existing_description.e_way_bill_no = item.get(
                                'e_way_bill_no', 0)
                            existing_description.save()
                            descriptions_to_update.append(existing_description)

                    # Set the descriptions after saving the object
                    obj.descriptions.set(
                        descriptions_to_add + descriptions_to_update)
                except json.JSONDecodeError:
                    print('Error decoding JSON')
                except ItemDetailsMaster.DoesNotExist:
                    print('ItemDetailsMaster not found')
                except QuotationTypes.DoesNotExist:
                    print('QuotationTypes not found')

            return redirect(request.path)

        else:
            form = self.get_form(request, obj=obj)(instance=obj)

        admin_form = AdminForm(form, self.get_fieldsets(
            request), self.prepopulated_fields)

        extra_context = extra_context or {}
        context_data = self.get_changeform_initial_data(request)
        descriptions = obj.descriptions.all()
        description_data = [{
            'id': desc.id,
            'description': desc.description if desc.description else None,
            'quantity': desc.quantity,
            'actual_weight': desc.actual_weight,
            'charged_weight': desc.charged_weight,
            'unit_type': desc.unit_type if desc.unit_type else None,
            'rate': desc.rate,
            'challan_no': desc.challan_no,
            'inv_value': desc.inv_value,
            'e_way_bill_no': desc.e_way_bill_no
        } for desc in descriptions]

        extra_context['description_data'] = description_data
        extra_context.update(context_data)
        extra_context.update({
            'form': form,
            'adminform': admin_form,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'save_as': self.save_as,
            'is_popup': request.GET.get('_popup', False),
            'to_field': request.GET.get('_to_field', ''),
            'media': self.media,
            'change': True,
        })
        # return render(request, "admin/custom_lr_booking_view.html", extra_context)
        return super().change_view(request, object_id, form_url, extra_context)

    def has_delete_permission(self, request, obj=None):
        return True

    def delete_view(self, request, object_id, extra_context=None):
        """
        Enables deletion of the object in the admin interface.
        """
        return super().delete_view(request, object_id, extra_context)
