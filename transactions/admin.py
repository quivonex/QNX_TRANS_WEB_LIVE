from django.contrib import admin
from .models import LoadTypes, PaidTypes, PayTypes, CollectionTypes, DeliveryTypes
from django.contrib.auth import get_user_model

User = get_user_model()


class LoadTypesAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'is_active')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('type_name', 'id')
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        # Set the created_by and updated_by fields
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(LoadTypes, LoadTypesAdmin)


class PaidTypesAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'is_active')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('type_name', 'id')
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        # Set the created_by and updated_by fields
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(PaidTypes, PaidTypesAdmin)


class PayTypesAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'is_active')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('type_name', 'id')
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        # Set the created_by and updated_by fields
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(PayTypes, PayTypesAdmin)


class CollectionTypesAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'is_active')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('type_name', 'id')
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        # Set the created_by and updated_by fields
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(CollectionTypes, CollectionTypesAdmin)


class DeliveryTypesAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'is_active')
    readonly_fields = ('created_by', 'created_at', 'updated_by', 'updated_at')
    search_fields = ('type_name', 'id')
    list_filter = ('is_active',)

    def save_model(self, request, obj, form, change):
        # Set the created_by and updated_by fields
        if not change:  # Creating a new record
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(DeliveryTypes, DeliveryTypesAdmin)
