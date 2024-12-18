from django.urls import path
from .views import (
    CompanyMasterView,CompanyMasterCreateAPIView, CompanyMasterPermanentDeleteAPIView, CompanyMasterRetrieveAPIView, CompanyMasterListAPIView, CompanyMasterSoftDeleteAPIView, CompanyMasterUpdateAPIView,ActiveCompanyMasterListAPIView,
    FinancialYearsCreateAPIView, FinancialYearsPermanentDeleteAPIView, FinancialYearsRetrieveAPIView, FinancialYearsListAPIView, FinancialYearsSoftDeleteAPIView, FinancialYearsUpdateAPIView, RegionMasterPermanentDeleteAPIView, 
    StateMasterCreateAPIView, StateMasterPermanentDeleteAPIView, StateMasterRetrieveAPIView, StateMasterListAPIView,
    RegionMasterCreateAPIView, RegionMasterRetrieveAPIView, RegionMasterListAPIView,RegionMasterSoftDeleteAPIView, RegionMasterUpdateAPIView,
    ActiveStateMasterListAPIView,ActiveRegionMasterListAPIView,ActiveFinancialYearsListAPIView, StateMasterSoftDeleteAPIView, StateMasterUpdateAPIView
)

urlpatterns = [
    # CompanyMaster URLs
    path('company-masters/', CompanyMasterView.as_view(), name='company-master'),
    path('company-masters/create/', CompanyMasterCreateAPIView.as_view(), name='company-master-create'),
    path('company-masters/retrieve/', CompanyMasterRetrieveAPIView.as_view(), name='company-master-retrieve'),
    path('company-masters/list/', CompanyMasterListAPIView.as_view(), name='company-master-list'),
    path('active-companies/', ActiveCompanyMasterListAPIView.as_view(), name='active-company-master-list'),
    path('company-masters/update/', CompanyMasterUpdateAPIView.as_view(), name='company-masters-update'),
    path('company-masters/soft-delete/', CompanyMasterSoftDeleteAPIView.as_view(), name='company-masters-soft-delete'),
    path('company-masters/permanent-delete/', CompanyMasterPermanentDeleteAPIView.as_view(), name='company-masters-permanent-delete'),


    # FinancialYears URLs
    path('financial-years/create/', FinancialYearsCreateAPIView.as_view(), name='financial-years-create'),
    path('financial-years/retrieve/', FinancialYearsRetrieveAPIView.as_view(), name='financial-years-retrieve'),
    path('financial-years/list/', FinancialYearsListAPIView.as_view(), name='financial-years-list'),
    path('active-financialyears/', ActiveFinancialYearsListAPIView.as_view(), name='active-financial-years-list'),
    path('financial-years/update/', FinancialYearsUpdateAPIView.as_view(), name='financial-years-update'),
    path('financial-years/soft-delete/', FinancialYearsSoftDeleteAPIView.as_view(), name='financial-years-soft-delete'),
    path('financial-years/permanent-delete/', FinancialYearsPermanentDeleteAPIView.as_view(), name='financial-years-permanent-delete'),


    # StateMaster URLs
    path('state-masters/create/', StateMasterCreateAPIView.as_view(), name='state-master-create'),
    path('state-masters/retrieve/', StateMasterRetrieveAPIView.as_view(), name='state-master-retrieve'),
    path('state-masters/list/', StateMasterListAPIView.as_view(), name='state-master-list'),
    path('active-states/', ActiveStateMasterListAPIView.as_view(), name='active-state-master-list'),
    path('state-masters/update/', StateMasterUpdateAPIView.as_view(), name='state-masters-update'),
    path('state-masters/soft-delete/', StateMasterSoftDeleteAPIView.as_view(), name='state-masters-soft-delete'),
    path('state-masters/permanent-delete/', StateMasterPermanentDeleteAPIView.as_view(), name='state-masters-permanent-delete'),


    # RegionMaster URLs
    path('region-masters/create/', RegionMasterCreateAPIView.as_view(), name='region-master-create'),
    path('region-masters/retrieve/', RegionMasterRetrieveAPIView.as_view(), name='region-master-retrieve'),
    path('region-masters/list/', RegionMasterListAPIView.as_view(), name='region-master-list'),
    path('active-regions/', ActiveRegionMasterListAPIView.as_view(), name='active-region-master-list'),
    path('region-masters/update/', RegionMasterUpdateAPIView.as_view(), name='region-masters-update'),
    path('region-masters/soft-delete/', RegionMasterSoftDeleteAPIView.as_view(), name='region-masters-soft-delete'),
    path('region-masters/permanent-delete/',  RegionMasterPermanentDeleteAPIView.as_view(), name='region-masters-permanent-delete'),

]
