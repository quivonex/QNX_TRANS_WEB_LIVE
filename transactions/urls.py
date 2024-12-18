from django.urls import path
from .views import CollectionTypesCreateView, CollectionTypesPermanentDeleteAPIView, CollectionTypesRetrieveActiveView, CollectionTypesRetrieveAllView, CollectionTypesRetrieveView, CollectionTypesSoftDeleteAPIView, CollectionTypesUpdateAPIView, DeliveryTypesCreateView, DeliveryTypesPermanentDeleteAPIView, DeliveryTypesRetrieveActiveView, DeliveryTypesRetrieveAllView, DeliveryTypesRetrieveView, DeliveryTypesSoftDeleteAPIView, DeliveryTypesUpdateAPIView, LoadTypesCreateView, LoadTypesPermanentDeleteAPIView, LoadTypesRetrieveActiveView, LoadTypesRetrieveAllView, LoadTypesRetrieveView, LoadTypesSoftDeleteAPIView, LoadTypesUpdateAPIView, PaidTypesCreateView, PaidTypesPermanentDeleteAPIView, PaidTypesRetrieveActiveView, PaidTypesRetrieveAllView, PaidTypesRetrieveView, PaidTypesSoftDeleteAPIView, PaidTypesUpdateAPIView, PayTypesCreateView, PayTypesPermanentDeleteAPIView, PayTypesRetrieveActiveView, PayTypesRetrieveAllView, PayTypesRetrieveView, PayTypesSoftDeleteAPIView, PayTypesUpdateAPIView,CollectionTypesRetrieveForBookingMemoView,DeliveryTypesRetrieveForBookingMemoView

urlpatterns = [
    
     path('load-types/create/', LoadTypesCreateView.as_view(), name='load-types-create'),
     path('load-types/retrieve/', LoadTypesRetrieveView.as_view(), name='load-types-retrieve'),
     path('load-types/retrieve_all/', LoadTypesRetrieveAllView.as_view(), name='load-types-retrieve-all'),
     path('load-types/retrieve_active/', LoadTypesRetrieveActiveView.as_view(), name='load-types-retrieve-active'),
     path('load-types/update/', LoadTypesUpdateAPIView.as_view(), name='load-types-update'),
     path('load-types/soft-delete/', LoadTypesSoftDeleteAPIView.as_view(), name='load-types-soft-delete'),
     path('load-types/permanent-delete/', LoadTypesPermanentDeleteAPIView.as_view(), name='load-types-permanent-delete'),

     path('paid-types/create/', PaidTypesCreateView.as_view(), name='paid-types-create'),
     path('paid-types/retrieve/', PaidTypesRetrieveView.as_view(), name='paid-types-retrieve'),
     path('paid-types/retrieve_all/', PaidTypesRetrieveAllView.as_view(), name='paid-types-retrieve-all'),
     path('paid-types/retrieve_active/', PaidTypesRetrieveActiveView.as_view(), name='paid-types-retrieve-active'),
     path('paid-types/update/', PaidTypesUpdateAPIView.as_view(), name='paid-types-update'),
     path('paid-types/soft-delete/', PaidTypesSoftDeleteAPIView.as_view(), name='paid-types-soft-delete'),
     path('paid-types/permanent-delete/', PaidTypesPermanentDeleteAPIView.as_view(), name='paid-types-permanent-delete'),

     path('pay-types/create/', PayTypesCreateView.as_view(), name='pay-types-create'),
     path('pay-types/retrieve/', PayTypesRetrieveView.as_view(), name='pay-types-retrieve'),
     path('pay-types/retrieve_all/', PayTypesRetrieveAllView.as_view(), name='pay-types-retrieve-all'),
     path('pay-types/retrieve_active/', PayTypesRetrieveActiveView.as_view(), name='pay-types-retrieve-active'),
     path('pay-types/update/', PayTypesUpdateAPIView.as_view(), name='pay-types-update'),
     path('pay-types/soft-delete/', PayTypesSoftDeleteAPIView.as_view(), name='pay-types-soft-delete'),
     path('pay-types/permanent-delete/', PayTypesPermanentDeleteAPIView.as_view(), name='pay-types-permanent-delete'),

     path('collection-types/create/', CollectionTypesCreateView.as_view(), name='collection-types-create'),
     path('collection-types/retrieve/', CollectionTypesRetrieveView.as_view(), name='collection-types-retrieve'),
     path('collection-types/retrieve_all/', CollectionTypesRetrieveAllView.as_view(), name='collection-types-retrieve-all'),
     path('collection-types/retrieve_active/', CollectionTypesRetrieveActiveView.as_view(), name='collection-types-retrieve-active'),
     path('collection-types/retrieve_for_booking_memo/', CollectionTypesRetrieveForBookingMemoView.as_view(), name='collection-types-retrieve-for-booking-memo'),
     path('collection-types/update/', CollectionTypesUpdateAPIView.as_view(), name='collection-types-update'),
     path('collection-types/soft-delete/', CollectionTypesSoftDeleteAPIView.as_view(), name='collection-types-soft-delete'),
     path('collection-types/permanent-delete/',CollectionTypesPermanentDeleteAPIView.as_view(), name='collection-types-permanent-delete'),

     path('delivery-types/create/', DeliveryTypesCreateView.as_view(), name='delivery-types-create'),
     path('delivery-types/retrieve/', DeliveryTypesRetrieveView.as_view(), name='delivery-types-retrieve'),
     path('delivery-types/retrieve_all/', DeliveryTypesRetrieveAllView.as_view(), name='delivery-types-retrieve-all'),
     path('delivery-types/retrieve_active/', DeliveryTypesRetrieveActiveView.as_view(), name='delivery-types-retrieve-active'),
     path('delivery-types/retrieve_for_booking_memo/', DeliveryTypesRetrieveForBookingMemoView.as_view(), name='delivery-types-retrieve-for-booking-memo'),
     path('delivery-types/update/',DeliveryTypesUpdateAPIView.as_view(), name='delivery-types-update'),
     path('delivery-types/soft-delete/', DeliveryTypesSoftDeleteAPIView.as_view(), name='delivery-types-soft-delete'),
     path('delivery-types/permanent-delete/',DeliveryTypesPermanentDeleteAPIView.as_view(), name='delivery-types-permanent-delete'),


]
