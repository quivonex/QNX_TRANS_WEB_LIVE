from django.contrib import admin
from .models import ItemDetailsMaster, QuotationTypes
from django.contrib.auth import get_user_model

User = get_user_model()


class ItemDetailsMasterAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'description', 'is_active',
                    'created_by', 'created_at', 'updated_by', 'updated_at')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('item_name', 'description')
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        # Set the created_by and updated_by fields
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(ItemDetailsMaster, ItemDetailsMasterAdmin)


class QuotationTypesAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'is_active',
                    'created_by', 'created_at', 'updated_by', 'updated_at')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('type_name',)
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        # Set the created_by and updated_by fields
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(QuotationTypes, QuotationTypesAdmin)
