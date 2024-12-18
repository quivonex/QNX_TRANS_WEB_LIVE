from django.urls import path
from .views import (
    PartyTypesCreateAPIView,
    PartyTypesPermanentDeleteAPIView,
    PartyTypesRetrieveAPIView,
    PartyTypesListAPIView,
    PartyMasterCreateAPIView,
    PartyMasterRetrieveAPIView,
    PartyMasterListAPIView,
    PartyTypesRetrieveActiveView,
    PartyTypesSoftDeleteAPIView,
    PartyTypesUpdateAPIView,
    PartyMasterUpdateAPIView,
    PartyMasterRetrieveActiveView,
    PartyMasterSoftDeleteAPIView,
    PartyMasterPermanentDeleteAPIView,
    PartyMasterRetrieveByBranchView,
    PartyMasterRetrieveForPartyBillingView,
    PartyMasterFilterView
)

urlpatterns = [
    # PartyTypes URLs
    path('party-types/create/', PartyTypesCreateAPIView.as_view(), name='party-types-create'),
    path('party-types/retrieve/', PartyTypesRetrieveAPIView.as_view(), name='party-types-retrieve'),
    path('party-types/list/', PartyTypesListAPIView.as_view(), name='party-types-list'),
    path('party-types/retrieve_active/', PartyTypesRetrieveActiveView.as_view(), name='party-types-retrieve-active'),
    path('party-types/update/', PartyTypesUpdateAPIView.as_view(), name='party-types-update'),
    path('party-types/soft-delete/', PartyTypesSoftDeleteAPIView.as_view(), name='party-types-soft-delete'),
    path('party-types/permanent-delete/', PartyTypesPermanentDeleteAPIView.as_view(), name='party-types-permanent-delete'),


    # PartyMaster URLs
    path('party-master/create/', PartyMasterCreateAPIView.as_view(), name='party-master-create'),
    path('party-master/retrieve/', PartyMasterRetrieveAPIView.as_view(), name='party-master-retrieve'),
    path('party-master/list/', PartyMasterListAPIView.as_view(), name='party-master-list'),
    path('party-master/retrieve_active/', PartyMasterRetrieveActiveView.as_view(), name='party-master-retrieve-active'),
    path('party-master/retrieve_party_billing/', PartyMasterRetrieveForPartyBillingView.as_view(), name='party-master-retrieve-party_billing'),
    path('party-master/retrieve_by_branch/', PartyMasterRetrieveByBranchView.as_view(), name='party-master-retrieve-by-branch'),
    path('party-master/filter/', PartyMasterFilterView.as_view(), name='party-master-filter'),
    path('party-master/update/', PartyMasterUpdateAPIView.as_view(), name='party-master-update'),
    path('party-master/soft-delete/', PartyMasterSoftDeleteAPIView.as_view(), name='party-master-soft-delete'),
    path('party-master/permanent-delete/', PartyMasterPermanentDeleteAPIView.as_view(), name='party-master-permanent-delete'),

]
       
    
    