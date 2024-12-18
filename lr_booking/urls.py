
# lr_booking/urls.py

from django.urls import path
from .views import LR_Bokking_DescriptionCreateView, LR_Bokking_DescriptionPermanentDeleteAPIView, LR_Bokking_DescriptionRetrieveActiveView, LR_Bokking_DescriptionRetrieveAllView, LR_Bokking_DescriptionRetrieveView, LR_Bokking_DescriptionSoftDeleteAPIView, LR_Bokking_DescriptionUpdateAPIView, LR_BokkingCreateView, LR_BokkingPermanentDeleteAPIView, LR_BokkingRetrieveActiveView,LR_BokkingRetrieveLCMView, LR_BokkingRetrieveAllView, LR_BokkingRetrieveView, LR_BokkingSoftDeleteAPIView, LR_BokkingUpdateAPIView, LRBookingDeleteView, StandardRateCreateView, StandardRatePermanentDeleteAPIView, StandardRateRetrieveActiveView, StandardRateRetrieveAllView, StandardRateSoftDeleteAPIView, StandardRateUpdateAPIView, delete_lr_booking_description, get_consignor_details
from .views import  StandardRateRetrieveView,generate_invoice,generate_invoice_from_html,get_standard_rates,GenerateLRNumberView,GetStandardRateByWeight,LR_Other_ChargesCreateView,LR_Other_ChargesRetrieveView,LR_Other_ChargesRetrieveAllView,LR_Other_ChargesRetrieveActiveView,LR_Other_ChargesUpdateAPIView,LR_Other_ChargesSoftDeleteAPIView,LR_Other_ChargesPermanentDeleteAPIView,RetrieveLRBookingHistoryView,LR_BokkingRetrieveBookingMemoView,LR_BokkingRetrieveOnToBranchView,LR_BokkingRetrieveOnLrNumberView,LR_BokkingRetrieveLDMView,LR_BokkingRetrieveDSView,LRBookingFilterView,LR_BokkingRetrievePartyBillingView,LR_BokkingRetrieveVoucherReceiptView,LR_BokkingRetrieveMoneyReceiptView,LRCheckDSView,LRCheckLDMView,LRCheckBookingMemoView,LRPendingForLCMView,LRPendingForBookingMemoView,LRPendingForLDMView,LRPendingForDSView,LRPendingForPartyBillingView,LRPendingForVoucherReceiptView,LRPendingForMoneyReceiptView

urlpatterns = [
    # Other URL patterns
    path('delete/<int:pk>/', LRBookingDeleteView.as_view(),
         name='delete_lr_booking'),
    path('delete_lr_booking_description/<int:pk>/',
         delete_lr_booking_description, name='delete_lr_booking_description'),
    path('get-consignor-details/<int:consignor_id>/',
         get_consignor_details, name='get_consignor_details'),

     #     --------------------------------------------------------------------------

     path('standard-rate/create/', StandardRateCreateView.as_view(), name='standard-rate-create'),
     path('standard-rate/retrieve/', StandardRateRetrieveView.as_view(), name='standard-rate-retrieve'),
     path('standard-rate/retrieve_all/', StandardRateRetrieveAllView.as_view(), name='standard-rate-retrieve-all'),
     path('standard-rate/retrieve_active/', StandardRateRetrieveActiveView.as_view(), name='standard-rate-retrieve-active'),
     path('standard-rate/update/', StandardRateUpdateAPIView.as_view(), name='standard-rate-update'),
     path('standard-rate/soft-delete/', StandardRateSoftDeleteAPIView.as_view(), name='standard-rate-soft-delete'),
     path('standard-rate/permanent-delete/', StandardRatePermanentDeleteAPIView.as_view(), name='standard-rate-permanent-delete'),
     path('standard-rates-by-from-to-branch/', get_standard_rates.as_view()),
     path('standard-rates-by-from-to-branch-charged-weight/', GetStandardRateByWeight.as_view()),


     path('lr-bokking/generateLRNumber/', GenerateLRNumberView.as_view(), name='generate-lr-number'),
     path('lr-bokking/create/', LR_BokkingCreateView.as_view(), name='lr-bokking-create'),
     path('lr-bokking/retrieve/', LR_BokkingRetrieveView.as_view(), name='lr-bokking-retrieve'),
     path('lr-bokking/retrieve_all/', LR_BokkingRetrieveAllView.as_view(), name='lr-bokking-retrieve-all'),
     path('lr-bokking/retrieve_active/', LR_BokkingRetrieveActiveView.as_view(), name='lr-bokking-retrieve-lcm'),
     path('lr-bokking/retrieve_on_lr_number/', LR_BokkingRetrieveOnLrNumberView.as_view(), name='lr-bokking-retrieve_on_lr_number'),
     path('lr-bokking/retrieve_on_to_branch/', LR_BokkingRetrieveOnToBranchView.as_view(), name='lr-bokking-retrieve-on-to-branch'),
     path('lr-bokking/retrieve_LCM/', LR_BokkingRetrieveLCMView.as_view(), name='lr-bokking-retrieve-active'),
     path('lr-bokking/retrieve_LDM/', LR_BokkingRetrieveLDMView.as_view(), name='lr-bokking-retrieve-active-ldm'),
     path('lr-bokking/check_LDM/', LRCheckLDMView.as_view(), name='lr-bokking-check-ldm'),
     path('lr-bokking/filter/', LRBookingFilterView.as_view(), name='lr-bokking-retrieve-filter-lrs'),
     path('lr-bokking/retrieve_DS/', LR_BokkingRetrieveDSView.as_view(), name='lr-bokking-retrieve-active-ds'),
     path('lr-bokking/check_DS/', LRCheckDSView.as_view(), name='lr-bokking-check-ds'),
     path('lr-bokking/retrieve_party_billing/', LR_BokkingRetrievePartyBillingView.as_view(), name='lr-bokking-retrieve-active-party_billing'),
     path('lr-bokking/retrieve_voucher_receipt_branch/', LR_BokkingRetrieveVoucherReceiptView.as_view(), name='lr-bokking-retrieve-active-voucher_receipt_branch'),
     path('lr-bokking/retrieve_money_receipt/', LR_BokkingRetrieveMoneyReceiptView.as_view(), name='lr-bokking-retrieve-active-money_receipt'),
     path('lr-bokking/retrieve_Booking_memo/', LR_BokkingRetrieveBookingMemoView.as_view(), name='lr-bokking-retrieve-booking'),
     path('lr-bokking/check_Booking_memo/', LRCheckBookingMemoView.as_view(), name='lr-bokking-check-booking'),
     path('lr-bokking/retrieve-lr-booking-history/', RetrieveLRBookingHistoryView.as_view(), name='retrieve-lr-booking-history'),
     path('lr-bokking/update/', LR_BokkingUpdateAPIView.as_view(), name='lr-bokking-update'),
     path('lr-bokking/soft-delete/', LR_BokkingSoftDeleteAPIView.as_view(), name='lr-bokking-soft-delete'),
     path('lr-bokking/permanent-delete/', LR_BokkingPermanentDeleteAPIView.as_view(), name='lr-bokking-permanent-delete'),

     path('lr-bokking/pendency_LCM/', LRPendingForLCMView.as_view(), name='lr-bokking-pendency_LCM'),
     path('lr-bokking/pendency_BookingMemo/', LRPendingForBookingMemoView.as_view(), name='lr-bokking-pendency_BookingMemo'),
     path('lr-bokking/pendency_LDM/', LRPendingForLDMView.as_view(), name='lr-bokking-pendency_LDM'),
     path('lr-bokking/pendency_DS/', LRPendingForDSView.as_view(), name='lr-bokking-pendency_DS'),
     path('lr-bokking/pendency_PartyBilling/', LRPendingForPartyBillingView.as_view(), name='lr-bokking-pendency_PartyBilling'),
     path('lr-bokking/pendency_VoucherReceipt/', LRPendingForVoucherReceiptView.as_view(), name='lr-bokking-pendency_VoucherReceipt'),
     path('lr-bokking/pendency_MoneyReceipt/', LRPendingForMoneyReceiptView.as_view(), name='lr-bokking-pendency_MoneyReceipt'),


     path('invoice/<int:lr_no>/', generate_invoice.as_view(), name='generate_invoice'),
     path('new_invoice/', generate_invoice_from_html, name='generate_invoice'),
     path('lr-bokking-description/create/', LR_Bokking_DescriptionCreateView.as_view(), name='lr-bokking-description-create'),
     path('lr-bokking-description/retrieve/', LR_Bokking_DescriptionRetrieveView.as_view(), name='lr-bokking-description-retrieve'),
     path('lr-bokking-description/retrieve_all/', LR_Bokking_DescriptionRetrieveAllView.as_view(), name='lr-bokking-description-retrieve-all'),
     path('lr-bokking-description/retrieve_active/', LR_Bokking_DescriptionRetrieveActiveView.as_view(), name='lr-bokking-description-retrieve-active'),
     path('lr-bokking-description/update/', LR_Bokking_DescriptionUpdateAPIView.as_view(), name='lr-bokking-description-update'),
     path('lr-bokking-description/soft-delete/', LR_Bokking_DescriptionSoftDeleteAPIView.as_view(), name='lr-bokking-description-soft-delete'),
     path('lr-bokking-description/permanent-delete/',LR_Bokking_DescriptionPermanentDeleteAPIView.as_view(), name='lr-bokking-description-permanent-delete'),

     path('other-charges/create/', LR_Other_ChargesCreateView.as_view(), name='other-charges-create'),
     path('other-charges/retrieve/', LR_Other_ChargesRetrieveView.as_view(), name='other-charges-retrieve'),
     path('other-charges/retrieve_all/', LR_Other_ChargesRetrieveAllView.as_view(), name='other-charges-retrieve-all'),
     path('other-charges/retrieve_active/', LR_Other_ChargesRetrieveActiveView.as_view(), name='other-charges-retrieve-active'),
     path('other-charges/update/', LR_Other_ChargesUpdateAPIView.as_view(), name='other-charges-update'),
     path('other-charges/soft-delete/', LR_Other_ChargesSoftDeleteAPIView.as_view(), name='other-charges-soft-delete'),
     path('other-charges/permanent-delete/', LR_Other_ChargesPermanentDeleteAPIView.as_view(), name='other-charges-permanent-delete'),
    
]
  
