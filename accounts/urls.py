from django.urls import path
from .views import EffectTypesCreateView, EffectTypesPermanentDeleteAPIView, EffectTypesRetrieveAllView, EffectTypesRetrieveFilteredView, EffectTypesRetrieveView, EffectTypesSoftDeleteAPIView, EffectTypesUpdateAPIView, PaymentTypesCreateView, PaymentTypesPermanentDeleteAPIView, PaymentTypesRetrieveAllView, PaymentTypesRetrieveFilteredView, PaymentTypesRetrieveView, PaymentTypesSoftDeleteAPIView, PaymentTypesUpdateAPIView,ReceiptTypesCreateView, ReceiptTypesPermanentDeleteAPIView, ReceiptTypesRetrieveAllView, ReceiptTypesRetrieveFilteredView, ReceiptTypesRetrieveView, ReceiptTypesSoftDeleteAPIView, ReceiptTypesUpdateAPIView

urlpatterns = [
    # URL for listing and creating EffectTypes
     path('effect-types/create/', EffectTypesCreateView.as_view(), name='effect-types-create'),
     path('effect-types/retrieve/', EffectTypesRetrieveView.as_view(), name='effect-types-retrieve'),
     path('effect-types/retrieve-all/', EffectTypesRetrieveAllView.as_view(), name='effect-types-retrieve-all'),
     path('effect-types/retrieve-filtered/', EffectTypesRetrieveFilteredView.as_view(), name='effect-types-retrieve-filtered'),
     path('effect-types/update/', EffectTypesUpdateAPIView.as_view(), name='effect-types-update'),
     path('effect-types/soft-delete/', EffectTypesSoftDeleteAPIView.as_view(), name='effect-types-soft-delete'),
     path('effect-types/permanent-delete/', EffectTypesPermanentDeleteAPIView.as_view(), name='effect-types-permanent-delete'),

     # URL for listing and creating PamentTypes
     path('payment-types/create/', PaymentTypesCreateView.as_view(), name='payment-types-create'),
     path('payment-types/retrieve/', PaymentTypesRetrieveView.as_view(), name='payment-types-retrieve'),
     path('payment-types/retrieve-all/', PaymentTypesRetrieveAllView.as_view(), name='payment-types-retrieve-all'),
     path('payment-types/retrieve-filtered/', PaymentTypesRetrieveFilteredView.as_view(), name='payment-types-retrieve-filtered'),
     path('payment-types/update/', PaymentTypesUpdateAPIView.as_view(), name='payment-types-update'),
     path('payment-types/soft-delete/', PaymentTypesSoftDeleteAPIView.as_view(), name='payment-types-soft-delete'),
     path('payment-types/permanent-delete/', PaymentTypesPermanentDeleteAPIView.as_view(), name='payment-types-permanent-delete'),

     # URL for listing and creating ReceiptTypes
     path('receipt-types/', ReceiptTypesCreateView.as_view(), name='receipt-types-create'),
     path('receipt-types/retrieve/', ReceiptTypesRetrieveView.as_view(), name='receipt-types-retrieve'),
     path('receipt-types/retrieve-all/', ReceiptTypesRetrieveAllView.as_view(), name='receipt-types-retrieve-all'),
     path('receipt-types/retrieve-filtered/', ReceiptTypesRetrieveFilteredView.as_view(), name='receipt-types-retrieve-filtered'),
     path('receipt-types/update/', ReceiptTypesUpdateAPIView.as_view(), name='receipt-types-update'),
     path('receipt-types/soft-delete/', ReceiptTypesSoftDeleteAPIView.as_view(), name='receipt-types-soft-delete'),
     path('receipt-types/permanent-delete/', ReceiptTypesPermanentDeleteAPIView.as_view(), name='receipt-types-permanent-delete'),
]
         
    


  