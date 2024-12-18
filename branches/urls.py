from django.urls import path
from .views import (
    BranchMasterCreateAPIView, BranchMasterPermanentDeleteAPIView, BranchMasterRetrieveAPIView, BranchMasterListAPIView, ActiveBranchMasterListAPIView, BranchMasterSoftDeleteAPIView, BranchMasterUpdateAPIView, EmployeeMasterPermanentDeleteAPIView, EmployeeMasterSoftDeleteAPIView, EmployeeMasterUpdateAPIView,BranchStateRetrieveAPIView,
    EmployeeTypeCreateAPIView, EmployeeTypePermanentDeleteAPIView, EmployeeTypeRetrieveAPIView, EmployeeTypeListAPIView, ActiveEmployeeTypeListAPIView,
    EmployeeMasterCreateAPIView, EmployeeMasterRetrieveAPIView, EmployeeMasterListAPIView, ActiveEmployeeMasterListAPIView, EmployeeTypeSoftDeleteAPIView, EmployeeTypeUpdateAPIView,
    BranchMasterFilterView,EmployeeMasterFilterView
)

urlpatterns = [
    # URL for listing and creating BranchMaster
    path('branch/create/', BranchMasterCreateAPIView.as_view(), name='branch-create'),
    path('branch/retrieve/', BranchMasterRetrieveAPIView.as_view(), name='branch-retrieve'),
    path('branch/state/retrieve/', BranchStateRetrieveAPIView.as_view(), name='branch-state-retrieve'),
    path('branch/list/', BranchMasterListAPIView.as_view(), name='branch-list'),
    path('branch/active/', ActiveBranchMasterListAPIView.as_view(), name='branch-active-list'),
    path('branch/filter/', BranchMasterFilterView.as_view(), name='branch-filter'),
    path('branch/update/', BranchMasterUpdateAPIView.as_view(), name='branch-update'),
    path('branch/soft-delete/', BranchMasterSoftDeleteAPIView.as_view(), name='branch-soft-delete'),
    path('branch/permanent-delete/', BranchMasterPermanentDeleteAPIView.as_view(), name='branch-permanent-delete'),


    # URL for listing and creating EmployeeType
    path('employee-type/create/', EmployeeTypeCreateAPIView.as_view(), name='employee-type-create'),
    path('employee-type/retrieve/', EmployeeTypeRetrieveAPIView.as_view(), name='employee-type-retrieve'),
    path('employee-type/list/', EmployeeTypeListAPIView.as_view(), name='employee-type-list'),
    path('employee-type/active/', ActiveEmployeeTypeListAPIView.as_view(), name='employee-type-active-list'),
    path('employee-type/update/', EmployeeTypeUpdateAPIView.as_view(), name='employee-type-update'),
    path('employee-type/soft-delete/', EmployeeTypeSoftDeleteAPIView.as_view(), name='employee-type-soft-delete'),
    path('employee-type/permanent-delete/', EmployeeTypePermanentDeleteAPIView.as_view(), name='employee-type-permanent-delete'),


    # URL for listing and creating EmployeeMaster
    path('employee/create/', EmployeeMasterCreateAPIView.as_view(), name='employee-create'),
    path('employee/retrieve/', EmployeeMasterRetrieveAPIView.as_view(), name='employee-retrieve'),
    path('employee/list/', EmployeeMasterListAPIView.as_view(), name='employee-list'),
    path('employee/active/', ActiveEmployeeMasterListAPIView.as_view(), name='employee-active-list'),
    path('employee/filter/', EmployeeMasterFilterView.as_view(), name='employee-filter'),
    path('employee/update/', EmployeeMasterUpdateAPIView.as_view(), name='employee-update'),
    path('employee/soft-delete/', EmployeeMasterSoftDeleteAPIView.as_view(), name='employee-soft-delete'),
    path('employee/permanent-delete/', EmployeeMasterPermanentDeleteAPIView.as_view(), name='employee-permanent-delete'),

]



