from django.urls import path
from .views import (
    DriverMasterPermanentDeleteAPIView, OwnerMasterCreateAPIView, OwnerMasterRetrieveAPIView, OwnerMasterListAPIView,OwnerMasterActiveListAPIView, OwnerMasterSoftDeleteAPIView, OwnerMasterUpdateAPIView, OwnerMasterPermanentDeleteAPIView, VehicalMasterPermanentDeleteAPIView,
    VehicalTypesPermanentDeleteAPIView, VehicalTypesRetrieveAPIView, VehicalTypesListAPIView,VehicalTypesActiveListAPIView, VehicalTypesSoftDeleteAPIView, VehicalTypesUpdateAPIView,VehicalTypesCreateAPIView,
    VendorTypesCreateAPIView, VendorTypesPermanentDeleteAPIView, VendorTypesRetrieveAPIView, VendorTypesListAPIView,VendorTypesActiveListAPIView,VendorTypesSoftDeleteAPIView, VendorTypesUpdateAPIView,
    VehicalMasterCreateAPIView, VehicalMasterRetrieveAPIView, VehicalMasterListAPIView,VehicalMasterActiveListAPIView,VehicalMasterSoftDeleteAPIView, VehicalMasterUpdateAPIView,
    DriverMasterCreateAPIView, DriverMasterRetrieveAPIView, DriverMasterListAPIView,DriverMasterActiveListAPIView,DriverMasterSoftDeleteAPIView, DriverMasterUpdateAPIView,DriverMasterUpdateAvailableView,
    CheckDriverStatusView,CheckVehicleStatusView,EmailAPIView,OwnerMasterFilterView,VehicalMasterFilterView,DriverMasterFilterView
)

urlpatterns = [
    path('email/', EmailAPIView.as_view(), name='mail'),

    # OwnerMaster URLs
    path('owner/create/', OwnerMasterCreateAPIView.as_view(), name='owner-create'),
    path('owner/retrieve/', OwnerMasterRetrieveAPIView.as_view(), name='owner-retrieve'),
    path('owner/list/', OwnerMasterListAPIView.as_view(), name='owner-list'),
    path('owner/filter/', OwnerMasterFilterView.as_view(), name='owner-filter'),
    path('active-owner/', OwnerMasterActiveListAPIView.as_view(), name='active-owner-list'),
    path('owner/update/', OwnerMasterUpdateAPIView.as_view(), name='owner-update'),
    path('owner/soft-delete/', OwnerMasterSoftDeleteAPIView.as_view(), name='owner-soft-delete'),
    path('owner/permanent-delete/', OwnerMasterPermanentDeleteAPIView.as_view(), name='owner-permanent-delete'),


    # VehicalTypes URLs
    path('vehical-types/create/', VehicalTypesCreateAPIView.as_view(), name='vehical-types-create'),
    path('vehical-types/retrieve/', VehicalTypesRetrieveAPIView.as_view(), name='vehical-types-retrieve'),
    path('vehical-types/list/', VehicalTypesListAPIView.as_view(), name='vehical-types-list'),
    path('active-vehical-types/', VehicalTypesActiveListAPIView.as_view(), name='active-vehical-types-list'),
    path('vehical-types/update/', VehicalTypesUpdateAPIView.as_view(), name='vehical-types-update'),
    path('vehical-types/soft-delete/', VehicalTypesSoftDeleteAPIView.as_view(), name='vehical-types-soft-delete'),
    path('vehical-types/permanent-delete/', VehicalTypesPermanentDeleteAPIView.as_view(), name='vehical-types-permanent-delete'),


    # VendorTypes URLs
    path('vendor-types/create/', VendorTypesCreateAPIView.as_view(), name='vendor-types-create'),
    path('vendor-types/retrieve/', VendorTypesRetrieveAPIView.as_view(), name='vendor-types-retrieve'),
    path('vendor-types/list/', VendorTypesListAPIView.as_view(), name='vendor-types-list'),
    path('active-vendor-types/', VendorTypesActiveListAPIView.as_view(), name='active-vendor-types-list'),
    path('vendor-types/update/', VendorTypesUpdateAPIView.as_view(), name='vendor-types-update'),
    path('vendor-types/soft-delete/', VendorTypesSoftDeleteAPIView.as_view(), name='vendor-types-soft-delete'),
    path('vendor-types/permanent-delete/', VendorTypesPermanentDeleteAPIView.as_view(), name='vendor-types-permanent-delete'),


    # VehicalMaster URLs
    path('vehical-master/create/', VehicalMasterCreateAPIView.as_view(), name='vehical-master-create'),
    path('vehical-master/retrieve/', VehicalMasterRetrieveAPIView.as_view(), name='vehical-master-retrieve'),
    path('vehical-master/list/', VehicalMasterListAPIView.as_view(), name='vehical-master-list'),
    path('active-vehical-master/', VehicalMasterActiveListAPIView.as_view(), name='active-vehical-master-list'),
    path('vehical-master/filter/', VehicalMasterFilterView.as_view(), name='vehical-master-filter'),
    path('vehical-master/check/', CheckVehicleStatusView.as_view(), name='vehical-master-check'),
    path('vehical-master/update/', VehicalMasterUpdateAPIView.as_view(), name='vehical-master-update'),
    path('vehical-master/soft-delete/', VehicalMasterSoftDeleteAPIView.as_view(), name='vehical-master-soft-delete'),
    path('vehical-master/permanent-delete/', VehicalMasterPermanentDeleteAPIView.as_view(), name='vehical-master-permanent-delete'),


    # DriverMaster URLs
    path('driver-master/create/', DriverMasterCreateAPIView.as_view(), name='driver-master-create'),
    path('driver-master/retrieve/', DriverMasterRetrieveAPIView.as_view(), name='driver-master-retrieve'),
    path('driver-master/list/', DriverMasterListAPIView.as_view(), name='driver-master-list'),
    path('active-driver-master/', DriverMasterActiveListAPIView.as_view(), name='active-driver-master-list'),
    path('driver-master/filter/', DriverMasterFilterView.as_view(), name='driver-master-filter'),
    path('driver-master/check/', CheckDriverStatusView.as_view(), name='driver-master-check'),
    path('driver-master/update/', DriverMasterUpdateAPIView.as_view(), name='driver-master-update'),
    path('driver-master/update/is_available/', DriverMasterUpdateAvailableView.as_view(), name='driver-master-update-is-available'),
    path('driver-master/soft-delete/', DriverMasterSoftDeleteAPIView.as_view(), name='driver-master-soft-delete'),
    path('driver-master/permanent-delete/', DriverMasterPermanentDeleteAPIView.as_view(), name='driver-master-permanent-delete'),
    
]
