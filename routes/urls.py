# routes/urls.py
from django.urls import path
# from .views import calculate_distance_view
from .views import (
    RouteMasterCreateView, 
    RouteMasterRetrieveView, 
    RouteMasterRetrieveActiveAllView,
    RouteMasterRetrieveAllView, 
    RouteMasterUpdateAPIView, 
    RouteMasterSoftDeleteAPIView,
    RouteMasterRetrieveForBookingMemoView,
    ToBranchListByRouteAndFromBranchView,
    TripNumberRetrieveView,
    kmByRouteAndFromBranchandToBranchView,
    TripNumberRetrieveView2,
    TripNumberRetrieveView1,RouteMasterRetrieveActiveListAllView,RouteMasterFilterView
)

urlpatterns = [
    # path('', calculate_distance_view, name='calculate_distance'),
    path('route-master/create/', RouteMasterCreateView.as_view(), name='route-master-create'),
    path('route-master/retrieve/', RouteMasterRetrieveView.as_view(), name='route-master-retrieve'),
    path('route-master/retrieve-active/', RouteMasterRetrieveActiveAllView.as_view(), name='route-master-active-retrieve'),
    path('route-master/retrieve-active-list/', RouteMasterRetrieveActiveListAllView.as_view(), name='route-master-active-retrieve-list'),
    path('route-master/retrieve-booking_memo_data/', RouteMasterRetrieveForBookingMemoView.as_view(), name='route-master-booking_memo-retrieve'),
    path('route-master/get-to-branches/', ToBranchListByRouteAndFromBranchView.as_view(), name='get-to-branches'),
    path('route-master/get-stations-km/', kmByRouteAndFromBranchandToBranchView.as_view(), name='get-km'),
    path('route-master/get-trip-numbers/', TripNumberRetrieveView.as_view(), name='get-trip-numbers'),
    path('route-master/get-trip-numbers1/', TripNumberRetrieveView1.as_view(), name='get-trip-numbers1'),
    path('route-master/get-trip-numbers2/', TripNumberRetrieveView2.as_view(), name='get-trip-numbers2'),
    path('route-master/retrieve-all/', RouteMasterRetrieveAllView.as_view(), name='route-master-retrieve-all'),
    path('route-master/filter/', RouteMasterFilterView.as_view(), name='route-master-filter'),
    path('route-master/update/', RouteMasterUpdateAPIView.as_view(), name='route-master-update'),
    path('route-master/soft-delete/', RouteMasterSoftDeleteAPIView.as_view(), name='route-master-soft-delete'),
]
