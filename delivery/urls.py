from django.urls import path
from . import views
urlpatterns = [

    path('tur_status/create/', views.TURStatusCreateView.as_view()),
    path('tur_status/retrieve/', views.TURStatusRetrieveView.as_view()),
    path('tur_status/retrieve_all/', views.TURStatusRetrieveAllView.as_view()),
    path('tur_status/retrieve_active/', views.TURStatusRetrieveActiveView.as_view()),
    path('tur_status/update/', views.TURStatusUpdateAPIView.as_view()),
    path('tur_status/soft-delete/', views.TURStatusSoftDeleteAPIView.as_view()),
    path('tur_status/permanent-delete/', views.TURStatusPermanentDeleteAPIView.as_view()),
    
    path('tur/generateTURNumber/', views.GenerateTURNumberView.as_view(), name='generate_truck_unloading_report_number'),
    path('tur/create/', views.TURCreateView.as_view()),
    path('tur/retrieve/', views.TURRetrieveView.as_view()),
    path('tur/retrieve_all/', views.TURRetrieveAllView.as_view()),
    path('tur/retrieve_active/', views.TURRetrieveActiveView.as_view()),
    path('tur/filter/', views.TURFilterView.as_view(), name='tur-retrieve-filter-lrs'),
    path('tur/update/', views.TURUpdateAPIView.as_view()),
    path('tur/soft-delete/', views.TURSoftDeleteAPIView.as_view()),
    path('tur/permanent-delete/', views.TURPermanentDeleteAPIView.as_view()),
    
    path('lmd/generateLMDNumber/', views.GenerateLMDNumberView.as_view(), name='generate_LMD_number'),
    path('lmd/create/', views.CreateLDMView.as_view()),
    path('lmd/retrieve/', views.LMDRetrieveView.as_view()),
    path('lmd/retrieve_all/', views.LMDRetrieveAllView.as_view()),
    path('lmd/retrieve_active/', views.LMDRetrieveActiveView.as_view()),
    path('lmd/filter/', views.LmdFilterView.as_view(), name='lmd-retrieve-filter-lrs'),
    path('lmd/update/', views.UpdateLDMView.as_view()),
    path('lmd/soft-delete/', views.LMDSoftDeleteAPIView.as_view()),
    path('lmd/permanent-delete/', views.LMDPermanentDeleteAPIView.as_view()),
    
    path('ds/generateDSNumber/', views.GenerateDSNumberViews.as_view(), name='generate_DS_number'),
    path('ds/create/', views.CreateDeliveryStatementView.as_view()),
    path('ds/retrieve/', views.DSRetrieveView.as_view()),
    path('ds/retrieve_all/', views.DSRetrieveAllView.as_view()),
    path('ds/retrieve_active/', views.DSRetrieveActiveView.as_view()),
    path('ds/filter/', views.DSFilterView.as_view(), name='ds-retrieve-filter-lrs'),
    path('ds/update/', views.UpdateDeliveryStatementView.as_view()),
    path('ds/soft-delete/', views.DSSoftDeleteAPIView.as_view()),
    path('ds/permanent-delete/', views.DSPermanentDeleteAPIView.as_view()),

    path('cust_out_repo/retrieve/', views.CustomerOutstandingPendencyReport.as_view()),

    path('ds/<str:delivery_no>/', views.GenerateDeliveryStatementPDF.as_view()),
    path('lmd/<str:memo_no>/', views.GenerateLocalMemoDeliveryPDF.as_view(), name='local_memo_delivery_pdf'),
    path('tur/<str:tur_no>/', views.GenerateTruckUnloadingReportPDF.as_view(), name='truck_unloading_report_pdf'),
]