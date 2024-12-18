"""
URL configuration for transport_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
# from users.views import custom_login_view, redirect_admin_login
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users import views as user_views
from users.views import CustomTokenObtainPairView, ChangePasswordView, LoginReverifyAPIView,UserBranchesAPIView,CreateUserProfileView,GetUserByIdView,UserListView,UpdateUserProfileView,ResetPasswordView
from company.views import ActiveFinancialYearsListAPIView, FirstActiveCompanyMasterAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('routes.urls')),
    # path('admin/login/', redirect_admin_login, name='admin_login_redirect'),
    # path('login/', custom_login_view, name='login'),


    path('lr_booking/', include('lr_booking.urls')),
    path('branches/', include('branches.urls')),
    path('company/', include('company.urls')),
    path('vehicals/', include('vehicals.urls')),
    path('parties/', include('parties.urls')),
    path('accounts/', include('accounts.urls')), 
    path('account/', include('account.urls')), 
    path('items/', include('items.urls')), 
    path('destinations/', include('destinations.urls')),
    path('transactions/', include('transactions.urls')),
    path('collection/', include('collection.urls')),
    path('delivery/', include('delivery.urls')),
    path('routes/', include('routes.urls')),


    # path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/login/', CustomTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/reverify_login/', LoginReverifyAPIView.as_view(),
         name='token_obtain_pair'),
    path('api/financialyears/', ActiveFinancialYearsListAPIView.as_view(),
         name='active-financial-years-list'),
    path('api/company_info/', FirstActiveCompanyMasterAPIView.as_view(),
         name='active-company-info'),
    path('api/change-password/', ChangePasswordView.as_view(),
         name='change-password'),
    path('api/reset-password/', ResetPasswordView.as_view(),
         name='reset-password'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', user_views.RegisterUserView.as_view(), name='register'),
    path('api/create-user-profile/', CreateUserProfileView.as_view(), name='create_user_profile'),
    path('api/update-user-profile/', UpdateUserProfileView.as_view(), name='update_user_profile'),
    path('api/get-user-by-id/', GetUserByIdView.as_view(), name='get_user_by_id'),
    path('api/get-user-branches/', UserBranchesAPIView.as_view(), name='get_user_branches'),
    path('api/get-user-list/', UserListView.as_view(), name='get_user_list'),
    path('api/user-profile/', user_views.UserProfileView.as_view(),
         name='user_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
