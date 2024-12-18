from django.urls import path
from .views import get_branch_pincode,DestinationMasterCreateView, DestinationMasterPermanentDeleteAPIView, DestinationMasterRetrieveActiveView, DestinationMasterRetrieveAllView, DestinationMasterRetrieveView, DestinationMasterSoftDeleteAPIView, DestinationMasterUpdateAPIView,DestinationMasterRetrieveOnBranchView,DestinationMasterFilterView

urlpatterns = [
    # Other URL patterns
    path('get-branch-pincode/<int:branch_id>/',
         get_branch_pincode, name='get_branch_pincode'),
    path('destination/create/', DestinationMasterCreateView.as_view(), name='destination-create'),
    path('retrieve/', DestinationMasterRetrieveView.as_view(), name='destination-retrieve'),
    path('retrieve_all/', DestinationMasterRetrieveAllView.as_view(), name='destinatoion-retrieve-all'),
    path('destinations/retrieve_active/', DestinationMasterRetrieveActiveView.as_view(), name='destination-retrieve-active'),
    path('destination/filter/', DestinationMasterFilterView.as_view(), name='destinatoion-filter'),
    path('destination/update/', DestinationMasterUpdateAPIView.as_view(), name='destinatoion-update'),
    path('retrieve-destinations-on-branch/', DestinationMasterRetrieveOnBranchView.as_view(), name='retrieve_destinations_on_branch'),
    path('destination/soft-delete/', DestinationMasterSoftDeleteAPIView.as_view(), name='destinatoion-soft-delete'),
    path('destination/permanent-delete/', DestinationMasterPermanentDeleteAPIView.as_view(), name='destination-permanent-delete'),
]
