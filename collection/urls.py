from django.urls import path
from .views import GenerateCollectionPDF,generate_collection_pdf,GenerateCollectionMemo,BookingMemoLRsPermanentDeleteAPIView, BookingMemoLRsRetrieveAllView, BookingMemoLRsRetrieveFilteredView, BookingMemoLRsRetrieveView, BookingMemoLRsSoftDeleteAPIView, BookingMemoLRsUpdateAPIView, BookingMemoPermanentDeleteAPIView, BookingMemoRetrieveAllView, BookingMemoRetrieveFilteredView, BookingMemoRetrieveView, BookingMemoSoftDeleteAPIView, BookingMemoUpdateAPIView,CollectionGetCreateView, CollectionPermanentDeleteAPIView, CollectionRetrieveAllView, CollectionRetrieveFilteredView, CollectionRetrieveView, CollectionSoftDeleteAPIView, CollectionUpdateAPIView, CreateBookingMemoLRsView, CreateBookingMemoViews, CreateCollectionView,GenerateMemoNumberView
from .views import TripModeCreateView,TripModeRetrieveView,TripModeRetrieveAllView,TripModeRetrieveActiveView,TripModeUpdateAPIView,TripModeSoftDeleteAPIView,TripModePermanentDeleteAPIView,TripMemoCreateView,TripMemoUpdateView,TripMemoRetrieveAllView,TripMemoRetrieveActiveView,TripMemoSoftDeleteAPIView,TripMemoPermanentDeleteAPIView,TripMemoRetrieveView,BookingMemoRetrieveTripMemoView,GenerateTripNumberView,GenerateCollectionNumberView
from .views import (
    VehicalHireContractCreateView,VehicalHireContractRetrieveView,VehicalHireContractRetrieveAllView,VehicalHireContractRetrieveActiveView,VehicalHireContractUpdateAPIView,VehicalHireContractSoftDeleteAPIView,VehicalHireContractPermanentDeleteAPIView,GetVehicleHireContracts,GetVehicleHireContractByvehicalType,GenerateBookingMemoPDF,GenerateTripMemoPDF,BookingMemoLrslistRetrieveView,BookingMemoRetrieveTURView,
    CollectionFilterView,BookingMemoFilterView,TripMemoFilterView,BookingMemoPendingForTripMemoView,BookingMemoPendingForTURView,BrokerMasterCreateView,BrokerMasterUpdateView,
    BrokerMasterRetrieveView,BrokerMasterRetrieveAllView,BrokerMasterRetrieveActiveAllView,BrokerMasterSoftDeleteAPIView

)

urlpatterns = [
     path('collections/generateMemoNumber/', GenerateCollectionNumberView.as_view(), name='generate-memo-number'),
     path('collection/pdf/<int:memo_no>/', GenerateCollectionPDF.as_view()),
     path('new_invoice/', GenerateCollectionMemo.as_view(), name='generate_collection_memo'),
     path('collections/get-create/', CollectionGetCreateView.as_view(), name='collection-get-create'),
     path('collections/create/', CreateCollectionView.as_view(), name='create-collection'),
     path('collections/retrieve/', CollectionRetrieveView.as_view(), name='collections-retrieve'),
     path('collections/retrieve-all/', CollectionRetrieveAllView.as_view(), name='collections-retrieve-all'),
     path('collections/retrieve-filtered/', CollectionRetrieveFilteredView.as_view(), name='collections-retrieve-filtered'),
     path('collections/filter/', CollectionFilterView.as_view(), name='collections-retrieve-filter-lrs'),
     path('collections/update/', CollectionUpdateAPIView.as_view(), name='collections-update'),
     path('collections/soft-delete/', CollectionSoftDeleteAPIView.as_view(), name='collections-soft-delete'),
     path('collections/permanent-delete/', CollectionPermanentDeleteAPIView.as_view(), name='collections-permanent-delete'),

     path('booking-memo-lrs/create/', CreateBookingMemoLRsView.as_view(), name='create_booking_memo_lrs'),
     path('booking-memo-lrs/retrieve/', BookingMemoLRsRetrieveView.as_view(), name='booking-memo-lrs-retrieve'),
     path('booking-memo-lrs/retrieve-all/', BookingMemoLRsRetrieveAllView.as_view(), name='booking-memo-lrs-retrieve-all'),    
     path('booking-memo-lrs/update/', BookingMemoLRsUpdateAPIView.as_view(), name='booking-memo-lrs-update'),
     path('booking-memo-lrs/soft-delete/', BookingMemoLRsSoftDeleteAPIView.as_view(), name='booking-memo-lrs-soft-delete'),
     path('booking-memo-lrs/permanent-delete/', BookingMemoLRsPermanentDeleteAPIView.as_view(), name='booking-memo-lrs-permanent-delete'),

     path('generate_booking_memo_pdf/<int:memo_no>/', GenerateBookingMemoPDF.as_view(), name='generate_booking_memo_pdf'),
     path('booking-memo/generateMemoNumber/', GenerateMemoNumberView.as_view(), name='generate-memo-number'),
     path('booking-memo/create/', CreateBookingMemoViews.as_view(), name='create_booking_memo'),
     path('booking-memo/retrieve/', BookingMemoRetrieveView.as_view(), name='booking-memo-retrieve'),
     path('booking-memo/retrieve_trip_memo/', BookingMemoRetrieveTripMemoView.as_view(), name='booking-memo-retrieve'),
     path('booking-memo/retrieve_tur/', BookingMemoRetrieveTURView.as_view(), name='booking-memo-retrieve-tur'),
     path('booking-memo/retrieve-all/', BookingMemoRetrieveAllView.as_view(), name='booking-memo-retrieve-all'),
     path('booking-memo/retrieve-filtered/', BookingMemoRetrieveFilteredView.as_view(), name='booking-memo-retrieve-filtered'),
     path('booking-memo/filter/', BookingMemoFilterView.as_view(), name='booking-memo-retrieve-filter-lrs'),
     path('booking-memo/update/', BookingMemoUpdateAPIView.as_view(), name='booking-memo-update'),
     path('booking-memo/soft-delete/', BookingMemoSoftDeleteAPIView.as_view(), name='booking-memo-soft-delete'),
     path('booking-memo/permanent-delete/', BookingMemoPermanentDeleteAPIView.as_view(), name='booking-memo-permanent-delete'),
     path('booking-memo/retrieve-lrs/', BookingMemoLrslistRetrieveView.as_view()),
     path('booking-memo/pendency_trip/', BookingMemoPendingForTripMemoView.as_view(), name='booking-memo-pendency_trip'),
     path('booking-memo/pendency_tur/', BookingMemoPendingForTURView.as_view(), name='booking-memo-pendency_tru'),

     path('trip-mode/create/', TripModeCreateView.as_view(), name='trip-mode-create'),
     path('trip-mode/retrieve/', TripModeRetrieveView.as_view(), name='trip-mode-retrieve'),
     path('trip-mode/retrieve-all/', TripModeRetrieveAllView.as_view(), name='trip-mode-retrieve-all'), 
     path('trip-mode/retrieve-active/', TripModeRetrieveActiveView.as_view(), name='trip-mode-retrieve-active'),
     path('trip-mode/update/', TripModeUpdateAPIView.as_view(), name='trip-mode-update'),
     path('trip-mode/soft-delete/', TripModeSoftDeleteAPIView.as_view(), name='trip-mode-soft-delete'),
     path('trip-mode/permanent-delete/', TripModePermanentDeleteAPIView.as_view(), name='trip-mode-permanent-delete'),

     path('veh_hire_con/create/', VehicalHireContractCreateView.as_view(), name='create_vehicle_hire_contract'),
     path('veh_hire_con/retrieve/', VehicalHireContractRetrieveView.as_view(), name='retrieve_vehicle_hire_contract'),
     path('veh_hire_con/retrieve/all/', VehicalHireContractRetrieveAllView.as_view(), name='retrieve_all_vehicle_hire_contracts'),
     path('veh_hire_con/retrieve/active/', VehicalHireContractRetrieveActiveView.as_view(), name='retrieve_active_vehicle_hire_contracts'),
     path('veh_hire_con/update/', VehicalHireContractUpdateAPIView.as_view(), name='update_vehicle_hire_contract'),
     path('veh_hire_con/soft-delete/', VehicalHireContractSoftDeleteAPIView.as_view(), name='soft_delete_vehicle_hire_contract'),
     path('veh_hire_con/permanent-delete/', VehicalHireContractPermanentDeleteAPIView.as_view(), name='permanent_delete_vehicle_hire_contract'),
     path('veh_hire_con/get/', GetVehicleHireContracts.as_view(), name='get_vehicle_hire_contracts'),
     path('veh_hire_con/get-by-vehical-type/', GetVehicleHireContractByvehicalType.as_view(), name='get_vehicle_hire_contract_by_vehicaal_type'),

     path('generate_trip_memo_pdf/<str:trip_no>/', GenerateTripMemoPDF.as_view(), name='generate_trip_memo_pdf'),        
     path('trip-memo/generateTripNumber/', GenerateTripNumberView.as_view(), name='generate-trip-number'),
     path('trip-memo/create/', TripMemoCreateView.as_view(), name='create_trip_memo'),
     path('trip-memo/update/', TripMemoUpdateView.as_view(), name='update_trip_memo'),
     path('trip-memo/retrieve/', TripMemoRetrieveView.as_view(), name='trip-memo-retrieve-all'),
     path('trip-memo/retrieve-all/', TripMemoRetrieveAllView.as_view(), name='trip-memo-retrieve-all'),
     path('trip-memo/retrieve-active/', TripMemoRetrieveActiveView.as_view(), name='trip-memo-retrieve-active'),
     path('trip-memo/filter/', TripMemoFilterView.as_view(), name='trip-memo-retrieve-filter-lrs'),
     path('trip-memo/soft-delete/', TripMemoSoftDeleteAPIView.as_view(), name='trip-memo-soft-delete'),
     path('trip-memo/permanent-delete/', TripMemoPermanentDeleteAPIView.as_view(), name='trip-memo-permanent-delete'),

     path('brokere-master/create/', BrokerMasterCreateView.as_view(), name='create_broker_master'),
     path('brokere-master/update/', BrokerMasterUpdateView.as_view(), name='update_broker_master'),
     path('brokere-master/retrieve/', BrokerMasterRetrieveView.as_view(), name='broker_master-retrieve'),
     path('brokere-master/retrieve-all/', BrokerMasterRetrieveAllView.as_view(), name='broker_master-retrieve-all'),
     path('brokere-master/retrieve-active/', BrokerMasterRetrieveActiveAllView.as_view(), name='broker_master-retrieve-active'),
     path('brokere-master/soft-delete/', BrokerMasterSoftDeleteAPIView.as_view(), name='broker_master-soft-delete'),

]

