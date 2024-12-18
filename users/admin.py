# from django.contrib import admin
# from django.contrib.auth.models import User
# from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
# from .models import UserProfile
# from .forms import UserCreationForm

# # Unregister the default UserAdmin
# admin.site.unregister(User)


# class UserAdmin(DefaultUserAdmin):
#     add_form = UserCreationForm
#     form = UserCreationForm
#     model = User
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
#     list_filter = ('is_staff', 'is_superuser', 'is_active')

#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff',
#          'is_superuser', 'groups', 'user_permissions')}),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#     )

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'branch'),
#         }),
#     )


# admin.site.register(User, UserAdmin)

# # If you want to access UserProfile directly in admin
# admin.site.register(UserProfile)


# from django.contrib import admin
# from .models import UserProfile
# from django.core.exceptions import PermissionDenied


# @admin.register(UserProfile)
# class UserProfileAdmin(admin.ModelAdmin):
#     list_display = ('user', 'branch')
#     # Include other fields and configurations as needed

#     def save_model(self, request, obj, form, change):
#         if change:
#             # Ensure profile updates correctly
#             if obj.branch != getattr(request.user.userprofile, 'branch', None):
#                 raise PermissionDenied(
#                     "You cannot modify profiles of other branches.")
#         super().save_model(request, obj, form, change)


from django.contrib import admin
from .models import UserProfile
from django.core.exceptions import PermissionDenied


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_branches')
    # Allows multi-select interface in the admin
    filter_horizontal = ('branches',)

    def get_branches(self, obj):
        return ", ".join(branch.branch_name for branch in obj.branches.all())
    get_branches.short_description = 'Branches'

    def save_model(self, request, obj, form, change):
        if change:
            user_profile = UserProfile.objects.get(user=obj.user)
            if set(obj.branches.all()) != set(user_profile.branches.all()):
                if not request.user.is_superuser:
                    # Optional: Replace with your own permission logic
                    raise PermissionDenied(
                        "You do not have permission to modify branches for this user.")
        super().save_model(request, obj, form, change)
