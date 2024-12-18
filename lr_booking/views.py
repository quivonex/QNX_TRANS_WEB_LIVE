# lr_booking/views.py
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from .models import LR_Bokking, LR_Bokking_Description, PartyMaster
from django.http import JsonResponse


class LRBookingDeleteView(View):
    def get(self, request, *args, **kwargs):
        print(kwargs['pk'])
        booking = get_object_or_404(LR_Bokking, pk=kwargs['pk'])

        booking.delete()

        return redirect('admin:lr_booking_lr_bokking_changelist')


@csrf_exempt
def delete_lr_booking_description(request, pk):
    print(f"Attempting to delete item with id {pk}")
    if request.method == 'DELETE':
        description = get_object_or_404(LR_Bokking_Description, pk=pk)
        description.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)


def get_consignor_details(request, consignor_id):
    try:
        consignor = PartyMaster.objects.get(id=consignor_id)
        consignor_details = {
            'party_type': consignor.party_type.type_name,  # Adjust according to your model
            'party_name': consignor.party_name,
            'address': consignor.address,
            'area': consignor.area.destination_name,  # Adjust according to your model
            'contact_no': consignor.contact_no,
            'email_id': consignor.email_id,
        }
        print('Consignor details', consignor_details)
        return JsonResponse(consignor_details)
    except PartyMaster.DoesNotExist:
        return JsonResponse({'error': 'Consignor not found'}, status=404)



#-----------------------------------------------------------------------------------------------------

# lr_booking/views.py
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from .models import LR_Bokking, LR_Bokking_Description, PartyMaster
from django.http import JsonResponse


class LRBookingDeleteView(View):
    def get(self, request, *args, **kwargs):
        print(kwargs['pk'])
        booking = get_object_or_404(LR_Bokking, pk=kwargs['pk'])

        booking.delete()

        return redirect('admin:lr_booking_lr_bokking_changelist')


@csrf_exempt
def delete_lr_booking_description(request, pk):
    print(f"Attempting to delete item with id {pk}")
    if request.method == 'DELETE':
        description = get_object_or_404(LR_Bokking_Description, pk=pk)
        description.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'fail'}, status=400)


def get_consignor_details(request, consignor_id):
    try:
        consignor = PartyMaster.objects.get(id=consignor_id)
        consignor_details = {
            'party_type': consignor.party_type.type_name,  # Adjust according to your model
            'party_name': consignor.party_name,
            'address': consignor.address,
            'area': consignor.area.destination_name,  # Adjust according to your model
            'contact_no': consignor.contact_no,
            'email_id': consignor.email_id,
        }
        print('Consignor details', consignor_details)
        return JsonResponse(consignor_details)
    except PartyMaster.DoesNotExist:
        return JsonResponse({'error': 'Consignor not found'}, status=404)

#----------------------------------------------------------------------------------------

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import StandardRate,LR_Bokking,LR_Other_Charges
from .serializers import LR_BokkingDescriptionSerializer, LRBokkingSerializer, StandardRateSerializer,LR_Other_ChargesSerializer, BookingMemoSerializer, CollectionSerializer
from items.models import ItemDetailsMaster,QuotationTypes
from branches.models import BranchMaster
from vehicals.models import VehicalMaster
from parties.models import PartyMaster
from destinations.models import DestinationMaster
from transactions.models import LoadTypes, PaidTypes, CollectionTypes, DeliveryTypes,PayTypes
from django.core.exceptions import ObjectDoesNotExist
from company.models import CompanyMaster,FinancialYears
from django.http import HttpResponse
from rest_framework.exceptions import NotFound
from django.shortcuts import render, get_object_or_404
import json
from weasyprint import HTML, CSS
import base64
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
from datetime import datetime
from collection.models import Collection,BookingMemo,BookingMemoLRs, TripBokkingMemos, TripMemo
from collection.serializers import TripMemoSerializer
from delivery.models import LocalMemoDelivery,DeliveryStatement, TruckUnloadingReport,TruckUnloadingReportDetails
from delivery.serializers import TruckUnloadingReportSerializer,LocalMemoDeliverySerializer,DeliveryStatementSerializer
from rest_framework.exceptions import ValidationError
from users.models import UserProfile
from company.filters import apply_filters
from company.views import send_email_with_attachment
import os
from account.models import PartyBilling,VoucherReceiptBranch,MoneyReceipt,VoucherPaymentBranch
from account.serializers import PartyBillingSerializer,VoucherReceiptBranchSerializer,MoneyReceiptSerializer,VoucherPaymentBranchSerializer
from django.db.models import Q
from rest_framework.permissions import AllowAny
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models import F


class StandardRateCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the request data
            serializer = StandardRateSerializer(data=request.data)
            
            # Validate the serializer
            if serializer.is_valid():
                # Save the instance with the user from the request
                serializer.save(created_by=request.user)
                
                # Return a success response with the serialized data
                return Response({
                    'message': 'Standard Rate created successfully!',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'message': 'Error creating Standard Rate',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'message': 'An unexpected error occurred.',
                'status': 'error',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StandardRateRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        standard_rate_id = request.data.get('id')

        # Check if 'id' is provided
        if not standard_rate_id:
            return Response({
                'message': 'Standard Rate ID is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the StandardRate instance
            standard_rate = StandardRate.objects.get(id=standard_rate_id)
        except StandardRate.DoesNotExist:
            return Response({
                'message': 'Standard Rate not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = StandardRateSerializer(standard_rate)

        # Return the data with success status
        return Response({
            'message': 'Standard Rate retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    
class StandardRateRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = StandardRate.objects.filter(flag=True).order_by('-id')

            # Serialize the items data
            serializer = StandardRateSerializer(items, many=True)

            # Return a success response with the items data
            return Response({
                "status": "success",
                "message": "Items retrieved successfully.",
                "data": [serializer.data]
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                "status": "error",
                "message": "An unexpected error occurred.",
                "error": str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class StandardRateRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter the queryset for active StandardRate instances
            queryset = StandardRate.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = StandardRateSerializer(queryset, many=True)

            # Prepare the response data
            response_data = {
                'msg': 'StandardRate retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'msg': 'An unexpected error occurred',
                'status': 'error',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class StandardRateUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        driver_master_id = request.data.get('id')
        
        if not driver_master_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the StandardRate instance
            instance = StandardRate.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = StandardRateSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'StandardRate updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update StandardRate',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except StandardRate.DoesNotExist:
            return Response({
                'msg': 'StandardRate not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class StandardRateSoftDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        driver_master_id = request.data.get('id')
        
        if not driver_master_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the StandardRate instance
            instance = StandardRate.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'StandardRate deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except StandardRate.DoesNotExist:
            return Response({
                'msg': 'StandardRate not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class StandardRatePermanentDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        receipt_type_id = request.data.get('id')
        
        if not receipt_type_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the StandardRate instance
            instance = StandardRate.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'StandardRate permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except StandardRate.DoesNotExist:
            return Response({
                'msg': 'StandardRate not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class get_standard_rates(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'from_branch_id' and 'to_branch_id' in the POST data
        from_branch_id = request.data.get('from_branch_id')
        to_branch_id = request.data.get('to_branch_id')

        # Check if 'from_branch_id' and 'to_branch_id' are provided
        if not from_branch_id or not to_branch_id:
            return Response({
                'message': 'Both from_branch_id and to_branch_id are required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the first active StandardRate instance based on branch IDs
            standard_rate = StandardRate.objects.filter(
                from_branch_id=from_branch_id,
                to_branch_id=to_branch_id,
                is_active=True
            ).first()

            if not standard_rate:
                return Response({
                    'message': 'No active Standard Rate found for the provided branches',
                    'status': 'error',
                    'data':[]
                }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'message': 'Error fetching Standard Rate',
                'status': 'error',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Serialize the retrieved instance
        serializer = StandardRateSerializer(standard_rate)

        # Return the data with success status
        return Response({
            'message': 'Standard Rate retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)

class GetStandardRateByWeight(APIView):
    def post(self, request, *args, **kwargs):
        # Get 'from_branch_id', 'to_branch_id', and 'charged_weight' from the request data
        party = request.data.get('party')
        from_branch_id = request.data.get('from_branch_id')
        to_branch_id = request.data.get('to_branch_id')
        charged_weight = request.data.get('charged_weight')

        # Validate the presence of required fields
        if not from_branch_id or not to_branch_id:
            return Response({
                'message': 'Both from_branch_id and to_branch_id are required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate charged_weight is a number
        try:
            charged_weight = float(charged_weight)
        except (ValueError, TypeError):
            return Response({
                'message': 'Charged weight must be a valid number',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Filter StandardRate records based on branch IDs, is_active, and flag
            standard_rates = StandardRate.objects.filter(
                from_branch_id=from_branch_id,
                to_branch_id=to_branch_id,
                is_active=True,
                flag=True
            )

            # Apply party filter if provided and valid
            if party is not None and isinstance(party, str) and party.strip():
                standard_rates = standard_rates.filter(party_id=party)
            elif party is not None and isinstance(party, int):
                standard_rates = standard_rates.filter(party_id=party)

            if not standard_rates.exists():
                return Response({
                    'message': 'No active Standard Rate found for the provided branches',
                    'status': 'error',
                    'data': []
                }, status=status.HTTP_404_NOT_FOUND)

            # Find the record where charged_weight falls between 'up' and 'to'
            matched_rate = standard_rates.filter(
                up__lte=charged_weight,
                to__gte=charged_weight
            ).first()

            if not matched_rate:
                return Response({
                    'message': 'No Standard Rate found for the provided charged weight',
                    'status': 'error',
                    'data': []
                }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'message': 'Error fetching Standard Rate',
                'status': 'error',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Serialize and return the first matching record
        serializer = StandardRateSerializer(matched_rate)
        return Response({
            'message': 'Standard Rate retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
#------------------------------------------------------------------------------------------------------------------
class LR_Other_ChargesCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = LR_Other_ChargesSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response({
                    'message': 'LR Other Charges created successfully!',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            return Response({
                'message': 'Error creating LR Other Charges',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'message': 'An unexpected error occurred.',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LR_Other_ChargesRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        lr_other_charges_id = request.data.get('id')
        if not lr_other_charges_id:
            return Response({
                'message': 'LR Other Charges ID is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            lr_other_charges = LR_Other_Charges.objects.get(id=lr_other_charges_id)
        except LR_Other_Charges.DoesNotExist:
            return Response({
                'message': 'LR Other Charges not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = LR_Other_ChargesSerializer(lr_other_charges)
        return Response({
            'message': 'LR Other Charges retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)

class LR_Other_ChargesRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            items = LR_Other_Charges.objects.filter(flag=True).order_by('-id')
            serializer = LR_Other_ChargesSerializer(items, many=True)
            return Response({
                "status": "success",
                "message": "Items retrieved successfully.",
                "data": [serializer.data]
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": "error",
                "message": "An unexpected error occurred.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LR_Other_ChargesRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            queryset = LR_Other_Charges.objects.filter(is_active=True, flag=True).order_by('-id')
            serializer = LR_Other_ChargesSerializer(queryset, many=True)
            return Response({
                'msg': 'LR Other Charges retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'msg': 'An unexpected error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LR_Other_ChargesUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        lr_other_charges_id = request.data.get('id')
        if not lr_other_charges_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = LR_Other_Charges.objects.get(pk=lr_other_charges_id)
            serializer = LR_Other_ChargesSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'LR Other Charges updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            return Response({
                'msg': 'Failed to update LR Other Charges',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except LR_Other_Charges.DoesNotExist:
            return Response({
                'msg': 'LR Other Charges not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LR_Other_ChargesSoftDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        lr_other_charges_id = request.data.get('id')
        if not lr_other_charges_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = LR_Other_Charges.objects.get(pk=lr_other_charges_id)
            instance.flag = False
            instance.save()
            return Response({
                'msg': 'LR Other Charges deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        except LR_Other_Charges.DoesNotExist:
            return Response({
                'msg': 'LR Other Charges not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class LR_Other_ChargesPermanentDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        lr_other_charges_id = request.data.get('id')
        if not lr_other_charges_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = LR_Other_Charges.objects.get(pk=lr_other_charges_id)
            instance.delete()
            return Response({
                'msg': 'LR Other Charges permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        except LR_Other_Charges.DoesNotExist:
            return Response({
                'msg': 'LR Other Charges not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)   
# -----------------------------------------------------------------------------------------------------------------
def generate_barcode(lr_no):
    # Convert lr_no to string since barcode library expects a string
    lr_no_str = str(lr_no)

    # Create an in-memory bytes buffer to store the barcode image
    buffer = BytesIO()

    # Generate the barcode using CODE128 format without the text below
    CODE128 = barcode.get_barcode_class('code128')
    barcode_image = CODE128(lr_no_str, writer=ImageWriter())

    # Disable text rendering (don't show the LR number below the barcode)
    barcode_image.write(buffer, {'write_text': False})

    # Encode the barcode image to base64 so that it can be embedded in HTML
    buffer.seek(0)
    barcode_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return barcode_base64


class generate_invoice(APIView):
    def get(self, request, lr_no):
        try:
            # Fetch company details
            company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

            # Fetch LR_Booking details
            lr_booking = get_object_or_404(LR_Bokking, lr_no=lr_no)
            descriptions = lr_booking.descriptions.all()

            # Generate the barcode for the LR number
            barcode_base64 = generate_barcode(lr_no)

            # Get the logged-in user's name
            user_profile = UserProfile.objects.get(user=lr_booking.created_by)
            user_name = user_profile.first_name + " "+user_profile.last_name
            copies = list(range(4))
            # Render HTML to string
            html_string = render(request, 'invoices/invoice.html', {
                'company': company,
                'lr': lr_booking,
                'descriptions': descriptions,
                'barcode_base64': barcode_base64,
                'user_name': user_name,
                'copies': copies,
            }).content.decode('utf-8')

            # Define CSS for legal page size
            css = CSS(string='''
                @page {
                    size: 8.5in 15.5in;
                    margin: 5mm;
                }
                .page-break {
                    page-break-after: always;
                }
                .invoice-container {
                    height: 50%; 
                 
                    flex-direction: column;
                    justify-content: space-between;
                    # margin-top:50px;  
                }
            ''')

            # Convert HTML to PDF
            html = HTML(string=html_string)
            pdf = html.write_pdf(stylesheets=[css])

            # Return PDF response
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename=invoice_{lr_no}.pdf'

            # Check user's role and printing status
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.role == 'branch_manager':
                if lr_booking.printed_by_branch_manager:
                    return Response({"msg": "Invoice has already been printed by a branch manager.",'status': 'error'}, status=400)
                else:
                    lr_booking.printed_by_branch_manager = True
                    lr_booking.save()

            return response

        except Exception as e:
            # Log the error for debugging
            print(f"Error: {e}")
            return HttpResponse("Internal Server Error", status=500)

#----------------------------------------------------------------------------------

@csrf_exempt
def generate_invoice_from_html(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Extract the HTML content and LR number
            html_content = data.get('html')
            lr_no = data.get('lr_no')

            # Validate input
            if not html_content or not lr_no:
                return JsonResponse({'error': 'HTML content or LR number missing'}, status=400)

            # Fetch dynamic data based on LR number
            company = get_object_or_404(CompanyMaster, flag=True, is_active=True)
            lr_booking = get_object_or_404(LR_Bokking, lr_no=lr_no)
            descriptions = lr_booking.descriptions.all()  # Assuming this returns a queryset

            lr_number = lr_booking.lr_number    
            print("1",lr_booking.other_charge_1)
            print("2",lr_booking.other_charge_1.charges_name)
            # Generate dynamic data placeholders
            barcode_base64 = generate_barcode(lr_number)

            # Replace placeholders in the HTML content with actual dynamic data
            company_logo_url = request.build_absolute_uri(company.company_logo.url)
            html_content = html_content.replace('{{ company.company_logo }}', company_logo_url)
            html_content = html_content.replace('{{ company.company_name }}', company.company_name)
            html_content = html_content.replace('{{ company.slogan }}', company.slogan)
            html_content = html_content.replace('{{ company.address }}', company.address)
            html_content = html_content.replace('{{ company.contact_number }}', company.contact_number)
            html_content = html_content.replace('{{ company.GST_number }}', company.GST_number)
            html_content = html_content.replace('{{ barcode_base64 }}', barcode_base64)
            html_content = html_content.replace('{{ lr.branch.branch_name }}', str(lr_booking.branch.branch_name))
            html_content = html_content.replace('{{ lr.lr_number }}', str(lr_booking.lr_number))  # Ensure this is a string
            html_content = html_content.replace('{{ lr.load_type.type_name }}', str(lr_booking.load_type.type_name))
            html_content = html_content.replace('{{ lr.coll_vehicle.vehical_number }}', str(lr_booking.coll_vehicle.vehical_number))
            html_content = html_content.replace('{{ lr.coll_vehicle.vehical_type.type_name }}', str(lr_booking.coll_vehicle.vehical_type.type_name))
            html_content = html_content.replace('{{ lr.consignor }}', str(lr_booking.consignor))  # Convert to string if needed
            html_content = html_content.replace('{{ lr.consignor.address }}', str(lr_booking.consignor.address))
            html_content = html_content.replace('{{ lr.consignor.contact_no }}', str(lr_booking.consignor.contact_no))
            html_content = html_content.replace('{{ lr.consignor.email_id }}', str(lr_booking.consignor.email_id))
            html_content = html_content.replace('{{ lr.consignor.gst_no }}', str(lr_booking.consignee.gst_no))
            html_content = html_content.replace('{{ lr.consignee }}', str(lr_booking.consignee))  # Convert to string if needed
            html_content = html_content.replace('{{ lr.consignee.address }}', str(lr_booking.consignee.address))
            html_content = html_content.replace('{{ lr.consignee.contact_no }}', str(lr_booking.consignee.contact_no))
            html_content = html_content.replace('{{ lr.consignee.email_id }}', str(lr_booking.consignee.email_id))
            html_content = html_content.replace('{{ lr.consignee.gst_no }}', str(lr_booking.consignee.gst_no))
            html_content = html_content.replace('{{ lr.date }}', lr_booking.date.strftime('%Y-%m-%d'))
            html_content = html_content.replace('{{ lr.coll_vehicle }}', str(lr_booking.coll_vehicle))  # Convert to string if needed
            html_content = html_content.replace('{{ lr.tran_vehicle }}', str(lr_booking.tran_vehicle))
            html_content = html_content.replace('{{ lr.del_vehicle }}', str(lr_booking.del_vehicle))
            html_content = html_content.replace('{{ lr.coll_type }}', str(lr_booking.coll_type))
            html_content = html_content.replace('{{ lr.del_type }}', str(lr_booking.del_type))
            html_content = html_content.replace('{{ lr.coll_at }}', str(lr_booking.coll_at))
            html_content = html_content.replace('{{ lr.del_at }}', str(lr_booking.del_at))
            html_content = html_content.replace('{{ lr.from_branch }}', str(lr_booking.from_branch))
            html_content = html_content.replace('{{ lr.to_branch }}', str(lr_booking.to_branch))
            html_content = html_content.replace('{{ lr.billing_party }}', str(lr_booking.billing_party))
            html_content = html_content.replace('{{ lr.pay_type }}', str(lr_booking.pay_type))
            html_content = html_content.replace('{{ lr.freight }}', str(lr_booking.freight))
            html_content = html_content.replace('{{ lr.collection }}', str(lr_booking.collection))
            html_content = html_content.replace('{{ lr.coll_km }}', str(lr_booking.coll_km))
            html_content = html_content.replace('{{ lr.door_delivery }}', str(lr_booking.door_delivery))
            html_content = html_content.replace('{{ lr.del_km }}', str(lr_booking.del_km))
            html_content = html_content.replace('{{ lr.hamali }}', str(lr_booking.hamali))
            html_content = html_content.replace('{{ lr.hamali }}', str(lr_booking.hamali))
            html_content = html_content.replace('{{ lr.bilty_charges }}', str(lr_booking.bilty_charges))
            html_content = html_content.replace('{{ lr.godown_charges }}', str(lr_booking.godown_charges))   
            # html_content = html_content.replace('{{ lr.other_charge_1.charges_name }}', str(lr_booking.other_charge_1.charges_name))
            html_content = html_content.replace('{{ lr.other_charge_1_val }}', str(lr_booking.other_charge_1_val))
            # html_content = html_content.replace('{{ lr.other_charge_2.charges_name }}', str(lr_booking.other_charge_2.charges_name))
            html_content = html_content.replace('{{ lr.other_charge_2_val }}', str(lr_booking.other_charge_2_val))            
            html_content = html_content.replace('{{ lr.insurance_charges }}', str(lr_booking.insurance_charges))
            html_content = html_content.replace('{{ lr.e_way_bill_charges }}', str(lr_booking.e_way_bill_charges)) 
            html_content = html_content.replace('{{ lr.grand_total }}', str(lr_booking.grand_total))

            # Optionally loop over descriptions and append them to HTML content
            if descriptions:
                descriptions_html = ''.join([f'<li>{str(desc)}</li>' for desc in descriptions])  # Convert to string
                html_content = html_content.replace('{{ lr.descriptions }}', descriptions_html)

            css = CSS(string='''
                @page {
                    size: legal;
                    margin: 5mm;
                }
            ''')
            
            # Generate the PDF from the final HTML content
            html = HTML(string=html_content)
            pdf = html.write_pdf(stylesheets=[css])

            # Return the PDF as a response
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename=invoice_{lr_no}.pdf'
            return response

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# def generate_invoice(request, lr_no):
#     # Fetch company details
#     company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

#     # Fetch LR_Bokking details
#     lr_booking = get_object_or_404(LR_Bokking, lr_no=lr_no)
#     descriptions = lr_booking.descriptions.all()

#     # Render HTML to string
#     html_string = render(request, 'invoices/invoice.html', {
#         'company': company,
#         'lr': lr_booking,
#         'descriptions': descriptions,
#     }).content.decode('utf-8')

#     # Convert HTML to PDF
#     html = HTML(string=html_string)
#     pdf = html.write_pdf()

#     # Return PDF response
#     response = HttpResponse(pdf, content_type='application/pdf')
#     response['Content-Disposition'] = f'inline; filename=invoice_{lr_no}.pdf'
#     return response


# class LR_BokkingCreateView(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             # Extract descriptions from the request data
#             descriptions_ids = request.data.pop('descriptions', [])

#             # Initialize the serializer with the rest of the request data
#             serializer = LRBokkingSerializer(data=request.data)
            
#             # Validate the serializer
#             if serializer.is_valid():
#                 # Save the instance without descriptions
#                 lr_bokking = serializer.save(created_by=request.user)
                
#                 # Assign descriptions to the Many-to-Many field
#                 if descriptions_ids:
#                     lr_bokking.descriptions.set(descriptions_ids)

#                 return Response({
#                     'message': 'LR_Bokking created successfully!',
#                     'status': 'success',
#                     'data': LRBokkingSerializer(lr_bokking).data
#                 }, status=status.HTTP_201_CREATED)
            
#             # Return error response if validation fails
#             return Response({
#                 'message': 'Error creating LR_Bokking',
#                 'status': 'error',
#                 'errors': serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         except Exception as e:
#             # Handle unexpected exceptions
#             return Response({
#                 'message': 'An unexpected error occurred',
#                 'status': 'error',
#                 'error': str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class GenerateLRNumberView(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             financial_year_id = request.data.get('financial_year_id')
#             branch_id = request.data.get('branch_id')

#             if not financial_year_id or not branch_id:
#                 response_data = {
#                     'msg': 'financial_year_id and branch_id are required',
#                     'status': 'error',
#                     'data': None
#                 }
#                 return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

#             # Retrieve and validate the active financial year
#             financial_year = FinancialYears.objects.get(id=financial_year_id, is_active=True, flag=True)
#             financial_year_prefix = financial_year.year_name[-2:]

#             # Retrieve and validate the active branch
#             branch = BranchMaster.objects.get(id=branch_id, is_active=True, flag=True)
#             branch_code = branch.branch_code

#             # Combine the financial year prefix and branch code
#             prefix = f"{financial_year_prefix}{branch_code}"

#             # Get the last non-null and non-blank lr_number for this branch with matching financial year prefix
#             last_lr_booking = LR_Bokking.objects.filter(
#                 branch_id=branch_id,
#                 lr_number__startswith=prefix
#             ).exclude(lr_number__isnull=True).exclude(lr_number__exact='').order_by('-lr_number').first()

#             if last_lr_booking:
#                 last_sequence_number = int(last_lr_booking.lr_number[len(prefix):])
#                 new_lr_number = f"{prefix}{str(last_sequence_number + 1).zfill(5)}"
#             else:
#                 new_lr_number = f"{prefix}00001"

#             # On successful LR number generation
#             response_data = {
#                 'msg': 'LR number generated successfully',
#                 'status': 'success',
#                 'data': {
#                     'lr_number': new_lr_number
#                 }
#             }
#             return Response(response_data, status=status.HTTP_200_OK)

#         except ObjectDoesNotExist as e:
#             # Handle case where FinancialYear or BranchMaster doesn't exist
#             response_data = {
#                 'status': 'error',
#                 'message': 'The specified financial year or branch was not found.',
#                 'error': str(e)
#             }
#             return Response(response_data, status=status.HTTP_404_NOT_FOUND)

#         except ValueError as e:
#             # Handle cases where lr_number conversion fails or other value-related errors occur
#             response_data = {
#                 'status': 'error',
#                 'message': 'An error occurred during LR number generation due to invalid data.',
#                 'error': str(e)
#             }
#             return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             # Handle any other unexpected exceptions
#             response_data = {
#                 'status': 'error',
#                 'message': 'An error occurred while generating the LR number.',
#                 'error': str(e)
#             }
#             return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateLRNumberView(APIView):
    def post(self, request, *args, **kwargs):
        try:

            branch_id = request.data.get('branch_id')

            if not branch_id:
                response_data = {
                    'msg': 'branch_id are required',
                    'status': 'error',
                    'data': None
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


            # Retrieve and validate the active branch
            branch = BranchMaster.objects.get(id=branch_id, is_active=True, flag=True)
            branch_code = branch.branch_code

            # Combine the financial year prefix and branch code
            prefix = f"{branch_code}"

            # Get the last non-null and non-blank lr_number for this branch with matching financial year prefix
            last_lr_booking = LR_Bokking.objects.filter(
                branch_id=branch_id,
                lr_number__startswith=prefix
            ).exclude(lr_number__isnull=True).exclude(lr_number__exact='').order_by('-lr_number').first()

            if last_lr_booking:
                last_sequence_number = int(last_lr_booking.lr_number[len(prefix):])
                new_lr_number = f"{prefix}{str(last_sequence_number + 1).zfill(5)}"
            else:
                new_lr_number = f"{prefix}00001"

            # On successful LR number generation
            response_data = {
                'msg': 'LR number generated successfully',
                'status': 'success',
                'data': {
                    'lr_number': new_lr_number
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist as e:
            # Handle case where FinancialYear or BranchMaster doesn't exist
            response_data = {
                'status': 'error',
                'message': 'The specified branch was not found.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except ValueError as e:
            # Handle cases where lr_number conversion fails or other value-related errors occur
            response_data = {
                'status': 'error',
                'message': 'An error occurred during LR number generation due to invalid data.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any other unexpected exceptions
            response_data = {
                'status': 'error',
                'message': 'An error occurred while generating the LR number.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LR_BokkingCreateView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)

        branch_id = request.data.get("branch")
        from_branch_id = request.data.get("from_branch")
        if branch_id != from_branch_id:
                return Response({
                    "status": "error",
                    "msg": "Login Branch and From Branch must be the same."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Deserialize the incoming LR_Bokking data
        bokking_serializer = LRBokkingSerializer(data=request.data)
        if bokking_serializer.is_valid():
            # Create the LR_Bokking instance but don't save it yet
            lr_bokking_instance = bokking_serializer.create(validated_data=bokking_serializer.validated_data)

            # Get the 'serialized_table_data' from the request
            serialized_table_data = request.data.get('descriptions', None)

            descriptions_to_add = []

            if serialized_table_data:
                try:
                    # No need to call json.loads since serialized_table_data is already a list
                    table_data = serialized_table_data

                    for item in table_data:
                        if item.get('id') == 0:  # If the item doesn't have an id, create a new description
                            new_description = LR_Bokking_Description.objects.create(
                                description=ItemDetailsMaster.objects.get(pk=item['description']) if item.get('description') else None,
                                quantity=item.get('quantity', 0),
                                actual_weight=item.get('actual_weight', 0),
                                charged_weight=item.get('charged_weight', 0),
                                unit_type=QuotationTypes.objects.get(pk=item['unit_type']) if item.get('unit_type') else None,
                                rate=item.get('rate', 0),
                                challan_no=item.get('challan_no', 0),
                                inv_value=item.get('inv_value', 0),
                                e_way_bill_no=item.get('e_way_bill_no', None)
                            )
                            descriptions_to_add.append(new_description)
                        else:
                            # If the description exists, get the existing description
                            existing_description = LR_Bokking_Description.objects.get(pk=item['id'])
                            descriptions_to_add.append(existing_description)
                except ItemDetailsMaster.DoesNotExist:
                    return Response({"error": "ItemDetailsMaster not found"}, status=status.HTTP_400_BAD_REQUEST)
                except QuotationTypes.DoesNotExist:
                    return Response({"error": "QuotationTypes not found"}, status=status.HTTP_400_BAD_REQUEST)
                except LR_Bokking_Description.DoesNotExist:
                    return Response({"error": "LR_Bokking_Description not found"}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({
                        'msg': 'An error occurred',
                        'status': 'error',
                        'error': str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
          
            # Attach the LR_Bokking_Description objects to the LR_Bokking instance
            lr_bokking_instance.descriptions.set(descriptions_to_add)
            lr_bokking_instance.created_by = request.user
            # Save the main LR_Bokking object
            lr_bokking_instance.save()

            
            try:
                # Try to generate PDF and send email
                pdf_sent = True
                recipient_list = []
                email_addresses = [
                    lr_bokking_instance.consignor.email_id.strip(),
                    lr_bokking_instance.consignee.email_id.strip()
                ]            
                for email in email_addresses:
                    try:
                        validate_email(email)  
                        recipient_list.append(email)  
                    except ValidationError:                    
                        continue

                # Generate PDF
                lr_no = lr_bokking_instance.lr_no
                pdf_response = generate_invoice().get(request, lr_no)
                pdf_path = f"/tmp/invoice_{lr_no}.pdf"
                with open(pdf_path, 'wb') as pdf_file:
                    pdf_file.write(pdf_response.content)

                # Send email with PDF attachment
                subject = "Your LR Booking Confirmation"
                message = "Your LR is booked successfully. Please find the attached invoice."
                if recipient_list:
                    send_email_with_attachment(subject, message, recipient_list, pdf_path)

                # Remove temporary PDF file
                os.remove(pdf_path)
            except Exception as email_error:
                pdf_sent = False
                # Log or handle the error if needed
                print(f"Failed to send email or generate PDF: {str(email_error)}")

            # Return the serialized response of the newly created LR_Bokking object
            response_serializer = LRBokkingSerializer(lr_bokking_instance)
            if pdf_sent:
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    "status": "success",
                    "msg": "LR Booking created successfully, but failed to send email.",
                    "data":response_serializer.data
                }, status=status.HTTP_201_CREATED)

        return Response(bokking_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LR_BokkingRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        standard_rate_id = request.data.get('lr_no')

        # Check if 'id' is provided
        if not standard_rate_id:
            return Response({
                'message': 'LR_Bokking lr_no is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the LR_Bokking instance
            standard_rate = LR_Bokking.objects.get(lr_no=standard_rate_id)
        except LR_Bokking.DoesNotExist:
            return Response({
                'message': 'LR_Bokking not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = LRBokkingSerializer(standard_rate)        
        # Return the data with success status
        return Response({
            'message': 'LR_Bokking retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)

class LR_BokkingRetrieveOnLrNumberView(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        standard_rate_id = request.data.get('lr_number')

        # Check if 'id' is provided
        if not standard_rate_id:
            return Response({
                'message': 'LR_Bokking lr_number is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the LR_Bokking instance
            standard_rate = LR_Bokking.objects.get(lr_number=standard_rate_id)
        except LR_Bokking.DoesNotExist:
            return Response({
                'message': 'LR_Bokking not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = LRBokkingSerializer(standard_rate)        
        # Return the data with success status
        return Response({
            'message': 'LR_Bokking retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)

class LR_BokkingRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            branch_id = request.data.get("branch_id")
            if not branch_id:
                return Response({
                    "status": "error",
                    "message": "Branch ID is required."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user_profile = UserProfile.objects.get(user=request.user)            
            allowed_branches = user_profile.branches.all()
                        
            # Retrieve all items from the database
            items = LR_Bokking.objects.filter(
                flag=True,  
            ).filter(
                Q(branch__in=allowed_branches) | Q(from_branch__in=allowed_branches)  
            ).filter(
                Q(branch_id=branch_id) | Q(from_branch_id=branch_id)
            ).order_by('-lr_no')
            
            # Serialize the items data
            serializer = LRBokkingSerializer(items, many=True)
            
            # Return a success response with the items data
            return Response({
                "status": "success",
                "message": "LR_Bokking retrieved successfully.",
                "data": [serializer.data]
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                "status": "error",
                "message": "An unexpected error occurred",
                "error": str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class LR_BokkingRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all active items from the database
            queryset = LR_Bokking.objects.filter(is_active=True,flag=True).order_by('-lr_no')
            
            # Serialize the items data
            serializer = LRBokkingSerializer(queryset, many=True)
            
            # Return a success response with the items data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LR_BokkingRetrieveOnToBranchView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            to_branch_id = request.data.get('to_branch_id')
            if not to_branch_id:
                return Response({
                    'status': 'error',
                    'message': 'to_branch_id is required.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Retrieve all active items from the database
            queryset = LR_Bokking.objects.filter(is_active=True,flag=True,to_branch=to_branch_id).order_by('-lr_no')
            
            # Serialize the items data
            serializer = LRBokkingSerializer(queryset, many=True)
            
            # Return a success response with the items data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RetrieveLRBookingHistoryView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        # Expecting 'lr_number' in the POST data
        lr_number = request.data.get('lr_number')

        # Check if 'lr_number' is provided
        if not lr_number:
            return Response({
                'message': 'LR_Bokking lr_number is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the LR_Bokking instance by lr_number
            lr_booking = LR_Bokking.objects.get(lr_number=lr_number)

            # Fetch related collections
            collections = Collection.objects.filter(lr_booking=lr_booking)

            # Fetch related BookingMemoLRs and BookingMemo
            booking_memo_lrs = BookingMemoLRs.objects.filter(lr_booking=lr_booking)
            booking_memo = BookingMemo.objects.filter(lr_list__in=booking_memo_lrs).distinct()

            # Fetch related TripMemo
            trip_bokking_memos = TripBokkingMemos.objects.filter(booking_memo__in=booking_memo)
            trip_memo = TripMemo.objects.filter(booking_memos__in=trip_bokking_memos).distinct()

            # Fetch related TUR
            truck_unloading_report_details = TruckUnloadingReportDetails.objects.filter(lr_booking=lr_booking)
            truck_unloading_report = TruckUnloadingReport.objects.filter(tur_details__in=truck_unloading_report_details).distinct()

            # Fetch related LDM
            local_memo_delivery = LocalMemoDelivery.objects.filter(lr_booking=lr_booking)

            # Fetch related DS
            delivery_statement = DeliveryStatement.objects.filter(lr_booking=lr_booking)

            # Fetch related PartyBilling
            party_billing = PartyBilling.objects.filter(lr_booking=lr_booking)

            # Fetch related VoucherReceiptBranch
            voucher_reciept_branch = VoucherReceiptBranch.objects.filter(lr_booking=lr_booking)

            # Fetch related MoneyReceipt
            money_receipt = MoneyReceipt.objects.filter(lr_booking=lr_booking)
            
            # Fetch related VoucherPaymentBranch
            voucher_pay_branch = VoucherPaymentBranch.objects.filter(lr_no=lr_booking)

            # Serialize the data
            lr_booking_serializer = LRBokkingSerializer(lr_booking)
            collection_serializer = CollectionSerializer(collections, many=True)
            booking_memo_serializer = BookingMemoSerializer(booking_memo, many=True)
            trip_memo_serializer = TripMemoSerializer(trip_memo, many=True)
            truck_unloading_report_serializer = TruckUnloadingReportSerializer(truck_unloading_report,many=True)
            local_memo_delivery_serializer = LocalMemoDeliverySerializer(local_memo_delivery,many=True)
            delivery_statement_serializer = DeliveryStatementSerializer(delivery_statement,many=True)
            party_billing_serializer = PartyBillingSerializer(party_billing,many=True)
            voucher_reciept_branch_serializer = VoucherReceiptBranchSerializer(voucher_reciept_branch,many=True)
            money_receipt_serializer = MoneyReceiptSerializer(money_receipt,many=True)
            voucher_pay_branch_serializer = VoucherPaymentBranchSerializer(voucher_pay_branch,many=True)

            # Return the combined data
            return Response({
                'message': 'LR_Bokking history retrieved successfully',
                'status': 'success',
                'lr_booking': lr_booking_serializer.data,
                'collection_momo': collection_serializer.data,
                'booking_memos': booking_memo_serializer.data,
                'trip_memos': trip_memo_serializer.data,
                'truck_unloading_report':truck_unloading_report_serializer.data,
                'local_memo_delivery':local_memo_delivery_serializer.data,
                'delivery_statement':delivery_statement_serializer.data,
                'party_billing':party_billing_serializer.data,
                'voucher_reciept_branch':voucher_reciept_branch_serializer.data,
                'money_receipt':money_receipt_serializer.data,
                'voucher_pay_branch':voucher_pay_branch_serializer.data,

            }, status=status.HTTP_200_OK)

        except LR_Bokking.DoesNotExist:
            return Response({
                'message': 'LR_Bokking not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LR_BokkingRetrieveLCMView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            print("request data",request.data)
            # Extracting the required parameters from the request body
            from_branch_id = request.data.get('from_branch_id')
            date_str = request.data.get('date')
            
            # Parsing the date from the request
            if date_str:
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response({
                        'status': 'error',
                        'message': 'Invalid date format. Please use YYYY-MM-DD format.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'status': 'error',
                    'message': 'Date is required.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Fixed value for collection type (assuming coll_type id = 1 is fixed)
            fixed_coll_type_id = 1

            # Filtering the LR_Bokking queryset based on the provided parameters and fixed filters
            queryset = LR_Bokking.objects.filter(
                from_branch_id=from_branch_id,
                date=date,
                coll_type=fixed_coll_type_id,
                is_active=True,
                flag=True
            ).order_by('-lr_no')
            
            filtered_queryset = []
            for lr_booking in queryset:
                # Check if there are any Collections related to this LR_Bokking
                # where is_active=True and flag=True
                has_active_collection = Collection.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()

                # If no such collection exists, keep this LR_Bokking in the final list
                if not has_active_collection:
                    filtered_queryset.append(lr_booking)
            
            # Serialize the filtered queryset data
            serializer = LRBokkingSerializer(filtered_queryset, many=True)

            # # Serialize the filtered queryset data
            # serializer = LRBokkingSerializer(queryset, many=True)
            
            # Return success response with serialized data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

# class LR_BokkingRetrieveLDMView(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             # Extracting the required parameters from the request body
#             to_branch_id = request.data.get('to_branch_id')
#             if not to_branch_id:
#                 return Response({
#                     'message': 'LR_Bokking to_branch_id is required',
#                     'status': 'error'
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             # Fixed value for collection type (assuming coll_type id = 1 is fixed)
#             fixed_dell_type_id = 1

#             # Filtering the LR_Bokking queryset based on the provided parameters and fixed filters
#             queryset = LR_Bokking.objects.filter(
#                 to_branch_id=to_branch_id,           
#                 del_type=fixed_dell_type_id,
#                 is_active=True,
#                 flag=True
#             ).order_by('-lr_no')
            
#             filtered_queryset = []
#             for lr_booking in queryset:
#                 # Check if there are any has_active_delivery related to this LR_Bokking
#                 # where is_active=True and flag=True
#                 has_active_delivery = LocalMemoDelivery.objects.filter(
#                     lr_booking=lr_booking,
#                     is_active=True,
#                     flag=True
#                 ).exists()

#                 # If no such has_active_delivery exists, keep this LR_Bokking in the final list
#                 if not has_active_delivery:
#                     filtered_queryset.append(lr_booking)
            
#             # Serialize the filtered queryset data
#             serializer = LRBokkingSerializer(filtered_queryset, many=True)

#             # # Serialize the filtered queryset data
#             # serializer = LRBokkingSerializer(queryset, many=True)
            
#             # Return success response with serialized data
#             response_data = {
#                 'msg': 'LR_Bokking retrieved successfully',
#                 'status': 'success',
#                 'data': serializer.data
#             }
#             return Response(response_data, status=status.HTTP_200_OK)

#         except Exception as e:
#             # Handle unexpected exceptions
#             return Response({
#                 'status': 'error',
#                 'message': 'An unexpected error occurred',
#                 'error': str(e)  # Include the error message for debugging
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class LR_BokkingRetrieveLDMView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extracting the required parameters from the request body
            to_branch_id = request.data.get('to_branch_id')
            if not to_branch_id:
                return Response({
                    'message': 'LR_Bokking to_branch_id is required',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Fixed value for collection type (assuming coll_type id = 1 is fixed)
            fixed_dell_type_id = 1

            # Filtering the LR_Bokking queryset based on the provided parameters and fixed filters
            queryset = LR_Bokking.objects.filter(
                to_branch_id=to_branch_id,           
                del_type=fixed_dell_type_id,
                is_active=True,
                flag=True
            ).order_by('-lr_no')
            
            filtered_queryset = []
            for lr_booking in queryset:
                # Check for active deliveries
                has_active_delivery = LocalMemoDelivery.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()

                # Skip this LR_Bokking if it has active deliveries
                if has_active_delivery:
                    continue

                # # Validate TruckUnloadingReport completion
                # tur_reports = TruckUnloadingReport.objects.filter(
                #     tur_details__lr_booking=lr_booking
                # ).distinct()

                # # Ensure there are valid TURs for this LR_Bokking
                # valid_tur_reports = [
                #     tur for tur in tur_reports 
                #     if tur.is_active and tur.flag and lr_booking.to_branch_id == tur.branch_name_id
                # ]

                # # If no valid TURs exist, skip this LR_Bokking
                # if not valid_tur_reports:
                #     continue

                # Add to filtered queryset if all validations pass
                filtered_queryset.append(lr_booking)

            # Serialize the filtered queryset data
            serializer = LRBokkingSerializer(filtered_queryset, many=True)           
            # Return success response with serialized data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LRCheckLDMView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            lr_no = request.data.get('lr_no')
            if not lr_no:
                return Response({
                    "message": "LR number is required.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                lr_booking = LR_Bokking.objects.get(lr_no=lr_no)
            except LR_Bokking.DoesNotExist:
                return Response({
                    "message": f"LR Booking with lr_no {lr_booking.lr_number} does not exist.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validation 1: Check TruckUnloadingReport details
            tur_details = TruckUnloadingReportDetails.objects.filter(
                lr_booking=lr_booking
            ).prefetch_related('truckunloadingreport_set')

            valid_tur = False
            for detail in tur_details:
                if detail.truckunloadingreport_set.filter(is_active=True, flag=True).exists():
                    valid_tur = True
                    break

            if not valid_tur:
                return Response({
                    "message": f"LR {lr_booking.lr_number}: Truck Unloading Report is incomplete or missing.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            for tur_detail in tur_details:
                truck_unloading_reports = tur_detail.truckunloadingreport_set.filter(
                    is_active=True,
                    flag=True
                )
                if any(lr_booking.to_branch_id != tur.branch_name_id for tur in truck_unloading_reports):
                    return Response({
                        "message": f"LR {lr_booking.lr_number}: Unloading report branch mismatch.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)            

            return Response({
                "message": f"LR {lr_no}: All validations passed.",
                "status": "success"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": "An error occurred while checking the LR.",
                "status": "error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LR_BokkingRetrieveDSView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extracting the required parameters from the request body
            to_branch_id = request.data.get('to_branch_id')
            if not to_branch_id:
                return Response({
                    'message': 'LR_Bokking to_branch_id is required',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Filtering the LR_Bokking queryset based on the provided parameters and fixed filters
            queryset = LR_Bokking.objects.filter(
                to_branch_id=to_branch_id,
                is_active=True,
                flag=True
            ).order_by('-lr_no')

            validated_queryset = []
            for lr_booking in queryset:
                lr_no = lr_booking.lr_no  # Cache the LR number for validation

                # Validation 2: Check TruckUnloadingReport details
                tur_details = TruckUnloadingReportDetails.objects.filter(
                    lr_booking=lr_booking
                ).prefetch_related('truckunloadingreport_set')

                valid_tur = False
                for detail in tur_details:
                    if detail.truckunloadingreport_set.filter(is_active=True, flag=True).exists():
                        valid_tur = True
                        break

                if not valid_tur:
                    # Skip this lr_booking if TruckUnloadingReport is invalid
                    continue

                for tur_detail in tur_details:
                    truck_unloading_reports = tur_detail.truckunloadingreport_set.filter(
                        is_active=True,
                        flag=True
                    )
                    if any(lr_booking.to_branch_id != tur.branch_name_id for tur in truck_unloading_reports):
                        # Skip this lr_booking if any TruckUnloadingReport's branch does not match
                        continue

                # Validation 3: Check if del_type is LOCAL and validate LocalMemoDelivery
                if lr_booking.del_type_id == 1:  # Assuming 1 corresponds to "LOCAL"
                    local_memo_deliveries = LocalMemoDelivery.objects.filter(
                        lr_booking=lr_booking,
                        is_active=True,
                        flag=True
                    )
                    if not local_memo_deliveries.exists():
                        # Skip this lr_booking if LocalMemoDelivery is not completed
                        continue

                # # Validation 3: Check if Pay_type is Paid and validate CS/MR
                if lr_booking.pay_type_id  == 2:  # Assuming 1 corresponds to "ToPay"
                    exists_in_voucher_receipt_branch = VoucherReceiptBranch.objects.filter(
                        lr_booking=lr_booking,
                        is_active=True,
                        flag=True
                    ).exists()

                    # Check in MoneyReceipt
                    exists_in_money_receipt = MoneyReceipt.objects.filter(
                        lr_booking=lr_booking,
                        is_active=True,
                        flag=True
                    ).exists()
                    if not (exists_in_voucher_receipt_branch or exists_in_money_receipt):
                        # Skip this lr_booking if CS/MR is not completed
                        continue

                # If all validations pass, add the lr_booking to the validated list
                validated_queryset.append(lr_booking)

            validated_queryset = [
                # lr_booking for lr_booking in validated_queryset
                lr_booking for lr_booking in queryset
                if not  DeliveryStatement.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()
            ]   

            # Serialize the validated queryset data
            serializer = LRBokkingSerializer(validated_queryset, many=True)

            # Return success response with serialized data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LRCheckDSView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        try:
            lr_no = request.data.get('lr_no')
            if not lr_no:
                return Response({
                    "message": "LR number is required.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                lr_booking = LR_Bokking.objects.get(lr_no=lr_no)
            except LR_Bokking.DoesNotExist:
                return Response({
                    "message": f"LR Booking with lr_no {lr_booking.lr_number} does not exist.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validation 1: Check TruckUnloadingReport details
            tur_details = TruckUnloadingReportDetails.objects.filter(
                lr_booking=lr_booking
            ).prefetch_related('truckunloadingreport_set')

            valid_tur = False
            for detail in tur_details:
                if detail.truckunloadingreport_set.filter(is_active=True, flag=True).exists():
                    valid_tur = True
                    break

            if not valid_tur:
                return Response({
                    "message": f"LR {lr_booking.lr_number}: Truck Unloading Report is incomplete or missing.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            valid_branch = False
            for tur_detail in tur_details:
                truck_unloading_reports = tur_detail.truckunloadingreport_set.filter(
                    is_active=True,
                    flag=True
                )
                if any(tur.branch_name_id == lr_booking.to_branch_id for tur in truck_unloading_reports):
                    valid_branch = True
                    break

            if not valid_branch:
                return Response({
                    "message": f"LR {lr_booking.lr_number}: Unloading report branch mismatch.Means All TUR not Completed",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validation 2: Check LocalMemoDelivery for LOCAL delivery type
            if lr_booking.del_type_id == 1:  # Assuming 1 corresponds to "LOCAL"
                local_memo_deliveries = LocalMemoDelivery.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                )
                if not local_memo_deliveries.exists():
                    return Response({
                        "message": f"LR {lr_booking.lr_number}: Local Memo Delivery is incomplete.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

            # # Validation 3: Check payment details for ToPAY type
            # if lr_booking.pay_type_id == 2:  # Assuming 2 corresponds to "ToPAY"
            #     exists_in_voucher_receipt_branch = VoucherReceiptBranch.objects.filter(
            #         lr_booking=lr_booking,
            #         is_active=True,
            #         flag=True
            #     ).exists()

            #     exists_in_money_receipt = MoneyReceipt.objects.filter(
            #         lr_booking=lr_booking,
            #         is_active=True,
            #         flag=True
            #     ).exists()

            #     if not (exists_in_voucher_receipt_branch or exists_in_money_receipt):
            #         return Response({
            #             "message": f"LR {lr_booking.lr_number}: Payment details are incomplete.",
            #             "status": "error"
            #         }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "message": f"LR {lr_booking.lr_number}: All validations passed.",
                "status": "success"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": "An error occurred while checking the LR.",
                "status": "error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LR_BokkingRetrievePartyBillingView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extracting the required parameters from the request body
            billing_party = request.data.get('billing_party')
            if not billing_party:
                return Response({
                    'message': 'LR_Bokking billing_party is required',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Filtering the LR_Bokking queryset based on the provided parameters and fixed filters
            queryset = LR_Bokking.objects.filter(
                billing_party_id=billing_party,
                pay_type_id = 3,
                is_active=True,
                flag=True
            ).order_by('-lr_no')

            validated_queryset = [
                lr_booking for lr_booking in queryset
                if not  PartyBilling.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()
            ]   

            # Serialize the validated queryset data
            serializer = LRBokkingSerializer(validated_queryset, many=True)

            # Return success response with serialized data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LR_BokkingRetrieveVoucherReceiptView(APIView):
    def post(self, request, *args, **kwargs):
        try:            
            # Filtering the LR_Bokking queryset based on the provided parameters and fixed filters
            queryset = LR_Bokking.objects.filter(                
                pay_type_id__in=[1, 2],
                is_active=True,
                flag=True
            ).order_by('-lr_no')

            validated_queryset = [
                lr_booking for lr_booking in queryset
                if not  VoucherReceiptBranch.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()
            ]   

            # Serialize the validated queryset data
            serializer = LRBokkingSerializer(validated_queryset, many=True)

            # Return success response with serialized data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LR_BokkingRetrieveMoneyReceiptView(APIView):
    def post(self, request, *args, **kwargs):
        try:            
            # Filtering the LR_Bokking queryset based on the provided parameters and fixed filters
            queryset = LR_Bokking.objects.filter(                
                pay_type_id__in=[1, 2],
                is_active=True,
                flag=True
            ).order_by('-lr_no')

            validated_queryset = [
                lr_booking for lr_booking in queryset
                if not  MoneyReceipt.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()
            ]   

            # Serialize the validated queryset data
            serializer = LRBokkingSerializer(validated_queryset, many=True)

            # Return success response with serialized data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LR_BokkingRetrieveBookingMemoView(APIView):
    def post(self, request, *args, **kwargs):       
        try:
            # Extracting the required parameters from the request body
            from_branch_id = request.data.get('from_branch_id')
            to_branch_id = request.data.get('to_branch_id')
            
            # Ensure from_branch_id and to_branch_id are provided
            if not from_branch_id or not to_branch_id:
                return Response({
                    'status': 'error',
                    'message': 'from_branch_id and to_branch_id are required.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Filtering the LR_Bokking queryset based on the provided parameters
            queryset = LR_Bokking.objects.filter( 
                from_branch_id=from_branch_id, 
                to_branch_id=to_branch_id,              
                is_active=True,
                flag=True
            ).order_by('-lr_no')

            # Final list to store filtered LR_Bokking objects
            filtered_queryset = []

            for lr_booking in queryset:
                # Check if there are related BookingMemoLRs linked to this LR_Bokking
                has_related_booking_memo = BookingMemoLRs.objects.filter(
                    lr_booking=lr_booking
                ).exists()

                # Skip this LR_Bokking if it has related BookingMemoLRs with matching from_branch_id
                if has_related_booking_memo:
                    # Get related BookingMemos with the same conditions and relationships
                    related_booking_memos = BookingMemo.objects.filter(                       
                        lr_list__lr_booking=lr_booking,
                        is_active=True,
                        flag=True
                    )

                    # Check if any related BookingMemo has the same from_branch_id as the request
                    if any(memo.from_branch_id == from_branch_id for memo in related_booking_memos):
                        continue  # Skip this lr_booking as it meets the exclusion criteria

                # # Validation 2: Check if coll_type is LOCAL and validate Collection
                # if lr_booking.coll_type_id == 1:  # Assuming 1 corresponds to "LOCAL"
                #     collection = Collection.objects.filter(
                #         lr_booking=lr_booking,
                #         is_active=True,
                #         flag=True
                #     )
                #     if not collection.exists():
                #         # Skip this lr_booking if Collection is not completed
                #         continue

                # # # Validation 3: Check if Pay_type is Paid and validate CS/MR
                # if lr_booking.pay_type_id  == 1:  # Assuming 1 corresponds to "PAID"
                #     exists_in_voucher_receipt_branch = VoucherReceiptBranch.objects.filter(
                #         lr_booking=lr_booking,
                #         is_active=True,
                #         flag=True
                #     ).exists()

                #     # Check in MoneyReceipt
                #     exists_in_money_receipt = MoneyReceipt.objects.filter(
                #         lr_booking=lr_booking,
                #         is_active=True,
                #         flag=True
                #     ).exists()
                #     if not (exists_in_voucher_receipt_branch or exists_in_money_receipt):
                #         # Skip this lr_booking if CS/MR is not completed
                #         continue

                # Add this LR_Bokking to the filtered list if all conditions are met
                filtered_queryset.append(lr_booking)

            # Serialize and prepare the response data
            serializer = LRBokkingSerializer(filtered_queryset, many=True)
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LRCheckBookingMemoView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract lr_no from request
            lr_no = request.data.get('lr_no')
            if not lr_no:
                return Response({
                    "message": "LR number (lr_no) is required.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the LR_Bokking object
            try:
                lr_booking = LR_Bokking.objects.get(lr_no=lr_no)
            except LR_Bokking.DoesNotExist:
                return Response({
                    "message": f"LR_Bokking with lr_no {lr_booking.lr_number} does not exist.",
                    "status": "error"
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validation 2: Check if coll_type is LOCAL and validate Collection
            if lr_booking.coll_type_id == 1:  # Assuming 1 corresponds to "LOCAL"
                collection_exists = Collection.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()

                if not collection_exists:
                    return Response({
                        "message": f"LR {lr_booking.lr_number}: Collection not completed for LOCAL coll_type.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Validation 3: Check if pay_type is PAID and validate VoucherReceiptBranch/MoneyReceipt
            if lr_booking.pay_type_id == 1:  # Assuming 1 corresponds to "PAID"
                has_voucher_or_money_receipt = VoucherReceiptBranch.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists() or MoneyReceipt.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()

                if not has_voucher_or_money_receipt:
                    return Response({
                        "message": f"LR {lr_booking.lr_number}: CS/MR not completed for PAID pay_type.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

            # If all validations pass, return success message
            return Response({
                "message": f"LR {lr_booking.lr_number}: All validations passed successfully.",
                "status": "success"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                "message": "An unexpected error occurred during validation.",
                "status": "error",
                "error": str(e)  # Include the error for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LRBookingFilterView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(LR_Bokking, filters)

            # Serialize the filtered data
            serializer = LRBokkingSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class LR_BokkingUpdateAPIView(APIView):    
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        driver_master_id = request.data.get('lr_no')        
        if not driver_master_id:
            return Response({
                'msg': 'lr_no is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        branch_id = request.data.get("branch")
        from_branch_id = request.data.get("from_branch")
        if branch_id != from_branch_id:
                return Response({
                    "status": "error",
                    "msg": "Login Branch and From Branch must be the same."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the LR_Bokking instance
            instance = LR_Bokking.objects.get(pk=driver_master_id)

            # Check if grand_total is changing
            request_grand_total = request.data.get('grand_total')
            if request_grand_total is not None:
                request_grand_total = Decimal(request_grand_total)
                if instance.grand_total != request_grand_total:
                    # Validate related masters
                    if (
                        instance.voucher_receipt_branch_lr_bookings.filter(is_active=True, flag=True).exists() or
                        instance.money_receipt_lr_bookings.filter(is_active=True, flag=True).exists() or
                        instance.party_billing_lr_bookings.filter(is_active=True, flag=True).exists()
                    ):
                        return Response({
                            "status": "error",
                            "msg": (
                                "This LR payment is already done inside a related master "
                                "(VoucherReceiptBranch, MoneyReceipt, or PartyBilling). "
                                "You cannot change the amount of this LR."
                            )
                        }, status=status.HTTP_400_BAD_REQUEST)

            # Store the previous value of tchargedwt
            previous_tchargedwt = instance.tchargedwt or Decimal("0.00")            
            
            # Initialize serializer with the instance and updated data
            serializer = LRBokkingSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                # Save the updated instance
                serializer.save(updated_by=request.user)

                # Check if `tchargedwt` has changed
                updated_tchargedwt = Decimal(serializer.validated_data.get('tchargedwt', previous_tchargedwt))
                if updated_tchargedwt != previous_tchargedwt:
                    # Calculate the difference
                    difference = updated_tchargedwt - previous_tchargedwt

                    # Update related Collection objects
                    related_collections = instance.collections_lr_bookings.all()
                    for collection in related_collections:
                        collection.total_weight = F('total_weight') + difference
                        collection.save()

                    # Update related BookingMemo objects
                    related_booking_memo_lrs = instance.booking_memo_lr.all()
                    for booking_memo_lr in related_booking_memo_lrs:
                        booking_memo = booking_memo_lr.booking_memo_booking_memo_lrs.first()
                        if booking_memo:
                            booking_memo.total_weight = F('total_weight') + difference
                            booking_memo.save()

                            # Update related TripMemo objects
                            related_trip_booking_memos = booking_memo.tripbokkingmemos_set.all()
                            for trip_booking_memo in related_trip_booking_memos:
                                # Fetch all TripMemo objects related to the TripBokkingMemos
                                related_trip_memos = trip_booking_memo.tripmemo_set.all()
                                for trip_memo in related_trip_memos:
                                    trip_memo.total_weight = F('total_weight') + difference
                                    trip_memo.save()
                            
                            # Update related TruckUnloadingReport objects based on the memo_no (ForeignKey to BookingMemo)
                            related_truck_unloading_reports = booking_memo.truckunloadingreport_set.all()
                            for truck_unloading_report in related_truck_unloading_reports:
                                truck_unloading_report.total_weight = F('total_weight') + difference
                                truck_unloading_report.save()
                        
                    # Update related LDM objects
                    related_ldm = instance.delivery_lr_bookings.all()
                    for delevery in related_ldm:
                        delevery.total_weight = F('total_weight') + difference
                        delevery.save()
                    
                    # Update related DS objects
                    related_ds = instance.ds_lr_bookings.all()
                    for ds in related_ds:
                        ds.total_weight = F('total_weight') + difference
                        ds.save()
                        
                
                # Get the 'descriptions' from the request
                serialized_table_data = request.data.get('descriptions', None)               

                if serialized_table_data is not None:
                    # Fetch existing descriptions linked to the instance
                    existing_descriptions = list(instance.descriptions.all())                
                    # If the list is empty, delete all existing descriptions
                    if not serialized_table_data:  # If no new descriptions are provided                      
                        for desc in existing_descriptions:
                            desc.delete()
                        instance.descriptions.clear()  # Clear the relation
                    else:
                        # Create a map of existing description IDs for quick lookup
                        existing_description_ids = {desc.id for desc in existing_descriptions}
                        
                        # Extract new description IDs from the request
                        new_description_ids = {item.get('id') for item in serialized_table_data if item.get('id') != 0}
                        
                        # Identify descriptions to delete
                        descriptions_to_delete = [desc for desc in existing_descriptions if desc.id not in new_description_ids]
                        
                        # Delete descriptions that are no longer linked
                        for desc in descriptions_to_delete:
                            desc.delete()

                        # Initialize lists to keep track of new and updated descriptions
                        descriptions_to_add = []
                        descriptions_to_update = []

                        for item in serialized_table_data:
                            if item.get('id') == 0:  # New record
                                new_description = LR_Bokking_Description.objects.create(
                                    description=ItemDetailsMaster.objects.get(pk=item['description']) if item.get('description') else None,
                                    quantity=item.get('quantity', 0),
                                    actual_weight=item.get('actual_weight', 0),
                                    charged_weight=item.get('charged_weight', 0),
                                    unit_type=QuotationTypes.objects.get(pk=item['unit_type']) if item.get('unit_type') else None,
                                    rate=item.get('rate', 0),
                                    challan_no=item.get('challan_no', 0),
                                    inv_value=item.get('inv_value', 0),
                                    e_way_bill_no=item.get('e_way_bill_no', None)
                                )
                                descriptions_to_add.append(new_description)
                            else:  # Existing record
                                # Fetch and update the existing LR_Bokking_Description object
                                existing_description = LR_Bokking_Description.objects.get(pk=item['id'])
                                existing_description.description = ItemDetailsMaster.objects.get(pk=item['description']) if item.get('description') else None
                                existing_description.quantity = item.get('quantity', 0)
                                existing_description.actual_weight = item.get('actual_weight', 0)
                                existing_description.charged_weight = item.get('charged_weight', 0)
                                existing_description.unit_type = QuotationTypes.objects.get(pk=item['unit_type']) if item.get('unit_type') else None
                                existing_description.rate = item.get('rate', 0)
                                existing_description.challan_no = item.get('challan_no', 0)
                                existing_description.inv_value = item.get('inv_value', 0)
                                existing_description.e_way_bill_no = item.get('e_way_bill_no', None)
                                existing_description.save()
                                descriptions_to_update.append(existing_description)

                        # Set the descriptions after saving the object
                        instance.descriptions.set(descriptions_to_add + descriptions_to_update)
                    
                return Response({
                    'msg': 'LR_Bokking updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update LR_Bokking',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except LR_Bokking.DoesNotExist:
            return Response({
                'msg': 'LR_Bokking not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class LR_BokkingUpdateAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         # Extract ID from request data
#         driver_master_id = request.data.get('lr_no')

#         if not driver_master_id:
#             return Response({
#                 'msg': 'lr_no is required',
#                 'status': 'error',
#                 'data': {}
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # Retrieve the LR_Bokking instance
#             instance = LR_Bokking.objects.get(pk=driver_master_id)
            
#             # Initialize serializer with the instance and updated data
#             serializer = LRBokkingSerializer(instance, data=request.data, partial=True)
            
#             if serializer.is_valid():
#                 # Save the updated instance
#                 serializer.save(updated_by=request.user)
                
#                 # Get the 'descriptions' from the request
#                 serialized_table_data = request.data.get('descriptions', None)

#                 if serialized_table_data:
#                     try:
#                         # Fetch existing descriptions linked to the instance
#                         existing_descriptions = list(instance.descriptions.all())
                        
#                         # Create a map of existing description IDs for quick lookup
#                         existing_description_ids = {desc.id for desc in existing_descriptions}
                        
#                         # Extract new description IDs from the request
#                         new_description_ids = {item.get('id') for item in serialized_table_data if item.get('id') != 0}
                        
#                         # Identify descriptions to delete
#                         descriptions_to_delete = [desc for desc in existing_descriptions if desc.id not in new_description_ids]
                        
#                         # Delete descriptions that are no longer linked
#                         for desc in descriptions_to_delete:
#                             desc.delete()

#                         # Initialize lists to keep track of new and updated descriptions
#                         descriptions_to_add = []
#                         descriptions_to_update = []

#                         for item in serialized_table_data:
#                             if item.get('id') == 0:  # New record
#                                 new_description = LR_Bokking_Description.objects.create(
#                                     description=ItemDetailsMaster.objects.get(pk=item['description']) if item.get('description') else None,
#                                     quantity=item.get('quantity', 0),
#                                     actual_weight=item.get('actual_weight', 0),
#                                     charged_weight=item.get('charged_weight', 0),
#                                     unit_type=QuotationTypes.objects.get(pk=item['unit_type']) if item.get('unit_type') else None,
#                                     rate=item.get('rate', 0),
#                                     challan_no=item.get('challan_no', 0),
#                                     inv_value=item.get('inv_value', 0),
#                                     e_way_bill_no=item.get('e_way_bill_no', 0)
#                                 )
#                                 descriptions_to_add.append(new_description)
#                             else:  # Existing record
#                                 # Fetch and update the existing LR_Bokking_Description object
#                                 existing_description = LR_Bokking_Description.objects.get(pk=item['id'])
#                                 existing_description.description = ItemDetailsMaster.objects.get(pk=item['description']) if item.get('description') else None
#                                 existing_description.quantity = item.get('quantity', 0)
#                                 existing_description.actual_weight = item.get('actual_weight', 0)
#                                 existing_description.charged_weight = item.get('charged_weight', 0)
#                                 existing_description.unit_type = QuotationTypes.objects.get(pk=item['unit_type']) if item.get('unit_type') else None
#                                 existing_description.rate = item.get('rate', 0)
#                                 existing_description.challan_no = item.get('challan_no', 0)
#                                 existing_description.inv_value = item.get('inv_value', 0)
#                                 existing_description.e_way_bill_no = item.get('e_way_bill_no', 0)
#                                 existing_description.save()
#                                 descriptions_to_update.append(existing_description)

#                         print("descriptions_to_add",descriptions_to_add)
#                         # Set the descriptions after saving the object
#                         instance.descriptions.set(descriptions_to_add + descriptions_to_update)
                    
#                     except json.JSONDecodeError:
#                         return Response({"error": "Error decoding JSON"}, status=status.HTTP_400_BAD_REQUEST)
#                     except ItemDetailsMaster.DoesNotExist:
#                         return Response({"error": "ItemDetailsMaster not found"}, status=status.HTTP_400_BAD_REQUEST)
#                     except QuotationTypes.DoesNotExist:
#                         return Response({"error": "QuotationTypes not found"}, status=status.HTTP_400_BAD_REQUEST)

#                 return Response({
#                     'msg': 'LR_Bokking updated successfully',
#                     'status': 'success',
#                     'data': [serializer.data]
#                 }, status=status.HTTP_200_OK)
            
#             return Response({
#                 'msg': 'Failed to update LR_Bokking',
#                 'status': 'error',
#                 'errors': serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         except LR_Bokking.DoesNotExist:
#             return Response({
#                 'msg': 'LR_Bokking not found',
#                 'status': 'error',
#                 'data': {}
#             }, status=status.HTTP_404_NOT_FOUND)

class LR_BokkingSoftDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        driver_master_id = request.data.get('lr_no')
        
        if not driver_master_id:
            return Response({
                'msg': 'lr_no is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the LR_Bokking instance
            instance = LR_Bokking.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'LR_Bokking deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except LR_Bokking.DoesNotExist:
            return Response({
                'msg': 'LR_Bokking not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class LR_BokkingPermanentDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        receipt_type_id = request.data.get('lr_no')
        
        if not receipt_type_id:
            return Response({
                'msg': 'lr_no is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the LR_Bokking instance
            instance = LR_Bokking.objects.get(pk=receipt_type_id)
            
            # Delete associated LR_Bokking_Description objects
            instance.descriptions.all().delete()
            
            # Permanently delete the LR_Bokking instance
            instance.delete()
            
            return Response({
                'msg': 'LR_Bokking and associated descriptions permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except LR_Bokking.DoesNotExist:
            return Response({
                'msg': 'LR_Bokking not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)



#--------------------------------------------------------------------------------------------------------------------


        
class LR_Bokking_DescriptionCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the request data
            serializer = LR_BokkingDescriptionSerializer(data=request.data)
            
            # Validate the serializer
            if serializer.is_valid():
                # Save the instance with the user from the request
                serializer.save(created_by=request.user)
                
                # Return a success response with data and a custom message
                return Response({
                    'message': 'LR_Bokking_Description created successfully!',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return validation errors if the data is not valid
            return Response({
                'message': 'Error creating LR_Bokking_Description',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'message': 'An unexpected error occurred',
                'status': 'error',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LR_Bokking_DescriptionRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        standard_rate_id = request.data.get('id')

        # Check if 'id' is provided
        if not standard_rate_id:
            return Response({
                'message': 'LR_Bokking_Description ID is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the LR_Bokking_Description instance
            standard_rate = LR_Bokking_Description.objects.get(id=standard_rate_id)
        except LR_Bokking_Description.DoesNotExist:
            return Response({
                'message': 'LR_Bokking_Description not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = LR_BokkingDescriptionSerializer(standard_rate)

        # Return the data with success status
        return Response({
            'message': 'LR_Bokking_Description retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    
class LR_Bokking_DescriptionRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = LR_Bokking_Description.objects.filter(flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = LR_BokkingDescriptionSerializer(items, many=True)
            
            # Return a success response with the items data
            return Response({
                "status": "success",
                "message": "LR_Bokking_Description retrieved successfully.",
                "data": [serializer.data]
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                "status": "error",
                "message": "An unexpected error occurred",
                "error": str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class LR_Bokking_DescriptionRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter the queryset for active items
            queryset = LR_Bokking_Description.objects.filter(is_active=True,flag=True).order_by('-id')
            
            # Serialize the filtered queryset
            serializer = LR_BokkingDescriptionSerializer(queryset, many=True)
            
            # Return a success response with the serialized data
            response_data = {
                'msg': 'LR_Bokking_Description retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'msg': 'An unexpected error occurred',
                'status': 'error',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class LR_Bokking_DescriptionUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        driver_master_id = request.data.get('id')
        
        if not driver_master_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the LR_Bokking_Description instance
            instance = LR_Bokking_Description.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer =LR_BokkingDescriptionSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'LR_Bokking_Description updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update LR_Bokking_Description',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except LR_Bokking_Description.DoesNotExist:
            return Response({
                'msg': 'LR_Bokking_Description not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class LR_Bokking_DescriptionSoftDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        driver_master_id = request.data.get('id')
        
        if not driver_master_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the LR_Bokking_Description instance
            instance = LR_Bokking_Description.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'LR_Bokking_Description deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except LR_Bokking_Description.DoesNotExist:
            return Response({
                'msg': 'LR_Bokking_Description not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class LR_Bokking_DescriptionPermanentDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        receipt_type_id = request.data.get('id')
        
        if not receipt_type_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the LR_Bokking_Description instance
            instance = LR_Bokking_Description.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'LR_Bokking_Description permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except LR_Bokking_Description.DoesNotExist:
            return Response({
                'msg': 'LR_Bokking_Description not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
 



class LRPendingForLCMView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            print("request data", request.data)
            # Extracting the `from_branch_id` from the request body
            from_branch_id = request.data.get('from_branch_id')
            
            # Fixed value for collection type (assuming coll_type id = 1 is fixed)
            fixed_coll_type_id = 1

            # Base queryset with fixed filters
            queryset = LR_Bokking.objects.filter(
                coll_type=fixed_coll_type_id,
                is_active=True,
                flag=True
            ).order_by('-lr_no')

            # Apply `from_branch_id` filter only if it's provided
            if from_branch_id:
                queryset = queryset.filter(from_branch_id=from_branch_id)

            filtered_queryset = []
            for lr_booking in queryset:
                # Check if there are any Collections related to this LR_Bokking
                # where is_active=True and flag=True
                has_active_collection = Collection.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()

                # If no such collection exists, keep this LR_Bokking in the final list
                if not has_active_collection:
                    filtered_queryset.append(lr_booking)
            
            # Serialize the filtered queryset data
            serializer = LRBokkingSerializer(filtered_queryset, many=True)

            # Return success response with serialized data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully for pending LCM',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LRPendingForBookingMemoView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extracting the required parameters from the request body
            from_branch_id = request.data.get('from_branch_id')
            to_branch_id = request.data.get('to_branch_id')

            # Base queryset with fixed filters
            queryset = LR_Bokking.objects.filter(
                is_active=True,
                flag=True
            ).order_by('-lr_no')

            # Apply conditional filters based on provided branch IDs
            if from_branch_id and to_branch_id:
                queryset = queryset.filter(
                    from_branch_id=from_branch_id,
                    to_branch_id=to_branch_id
                )
            elif from_branch_id:
                queryset = queryset.filter(from_branch_id=from_branch_id)
            elif to_branch_id:
                queryset = queryset.filter(to_branch_id=to_branch_id)

            # Final list to store filtered LR_Bokking objects
            filtered_queryset = []

            for lr_booking in queryset:
                # Validation 1: Check for related BookingMemoLRs
                has_related_booking_memo = BookingMemoLRs.objects.filter(
                    lr_booking=lr_booking
                ).exists()

                if has_related_booking_memo:
                    related_booking_memos = BookingMemo.objects.filter(
                        lr_list__lr_booking=lr_booking,
                        is_active=True,
                        flag=True
                    )

                   # Skip if both `from_branch_id` and `to_branch_id` are present and match related memos
                    if from_branch_id and to_branch_id:
                        if any(memo.from_branch_id == from_branch_id or memo.to_branch_id == to_branch_id for memo in related_booking_memos):
                            continue

                    # Skip if only `from_branch_id` is present and matches related memos
                    if from_branch_id:
                        if any(memo.from_branch_id == from_branch_id for memo in related_booking_memos):
                            continue

                    # Skip if only `to_branch_id` is present and matches related memos
                    if to_branch_id:
                        if any(memo.to_branch_id == to_branch_id for memo in related_booking_memos):
                            continue

                    # Skip all if neither `from_branch_id` nor `to_branch_id` is present
                    if not from_branch_id and not to_branch_id:
                        continue

                # Add this LR_Bokking to the filtered list if all conditions are met
                filtered_queryset.append(lr_booking)

            # Serialize and prepare the response data
            serializer = LRBokkingSerializer(filtered_queryset, many=True)
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LRPendingForLDMView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extracting the optional parameter from the request body
            to_branch_id = request.data.get('to_branch_id')

            # Fixed value for collection type (assuming coll_type id = 1 is fixed)
            fixed_dell_type_id = 1

            # Base queryset with fixed filters
            queryset = LR_Bokking.objects.filter(
                del_type=fixed_dell_type_id,
                is_active=True,
                flag=True
            ).order_by('-lr_no')

            # Apply `to_branch_id` filter if present in the request
            if to_branch_id:
                queryset = queryset.filter(to_branch_id=to_branch_id)

            filtered_queryset = []
            for lr_booking in queryset:
                # Check for active deliveries
                has_active_delivery = LocalMemoDelivery.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()

                # Skip this LR_Bokking if it has active deliveries
                if has_active_delivery:
                    continue

                # # Validate TruckUnloadingReport completion (commented logic for future use)
                # tur_reports = TruckUnloadingReport.objects.filter(
                #     tur_details__lr_booking=lr_booking
                # ).distinct()

                # valid_tur_reports = [
                #     tur for tur in tur_reports 
                #     if tur.is_active and tur.flag and lr_booking.to_branch_id == tur.branch_name_id
                # ]

                # if not valid_tur_reports:
                #     continue

                # Add to filtered queryset if all validations pass
                filtered_queryset.append(lr_booking)

            # Serialize the filtered queryset data
            serializer = LRBokkingSerializer(filtered_queryset, many=True)

            # Return success response with serialized data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LRPendingForDSView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extracting the optional parameter from the request body
            to_branch_id = request.data.get('to_branch_id')

            # Base queryset with fixed filters
            queryset = LR_Bokking.objects.filter(
                is_active=True,
                flag=True
            ).order_by('-lr_no')

            # Apply `to_branch_id` filter if provided
            if to_branch_id:
                queryset = queryset.filter(to_branch_id=to_branch_id)

            validated_queryset = []
            for lr_booking in queryset:
                lr_no = lr_booking.lr_no  # Cache the LR number for validation

                # Validation 2: Check TruckUnloadingReport details
                tur_details = TruckUnloadingReportDetails.objects.filter(
                    lr_booking=lr_booking
                ).prefetch_related('truckunloadingreport_set')

                valid_tur = False
                for detail in tur_details:
                    if detail.truckunloadingreport_set.filter(is_active=True, flag=True).exists():
                        valid_tur = True
                        break

                if not valid_tur:
                    # Skip this lr_booking if TruckUnloadingReport is invalid
                    continue

                for tur_detail in tur_details:
                    truck_unloading_reports = tur_detail.truckunloadingreport_set.filter(
                        is_active=True,
                        flag=True
                    )
                    if any(lr_booking.to_branch_id != tur.branch_name_id for tur in truck_unloading_reports):
                        # Skip this lr_booking if any TruckUnloadingReport's branch does not match
                        continue

                # Validation 3: Check if del_type is LOCAL and validate LocalMemoDelivery
                if lr_booking.del_type_id == 1:  # Assuming 1 corresponds to "LOCAL"
                    local_memo_deliveries = LocalMemoDelivery.objects.filter(
                        lr_booking=lr_booking,
                        is_active=True,
                        flag=True
                    )
                    if not local_memo_deliveries.exists():
                        # Skip this lr_booking if LocalMemoDelivery is not completed
                        continue

                # # Validation 4: Check if Pay_type is Paid and validate CS/MR
                # if lr_booking.pay_type_id == 2:  # Assuming 2 corresponds to "Paid"
                #     exists_in_voucher_receipt_branch = VoucherReceiptBranch.objects.filter(
                #         lr_booking=lr_booking,
                #         is_active=True,
                #         flag=True
                #     ).exists()

                #     # Check in MoneyReceipt
                #     exists_in_money_receipt = MoneyReceipt.objects.filter(
                #         lr_booking=lr_booking,
                #         is_active=True,
                #         flag=True
                #     ).exists()

                #     if not (exists_in_voucher_receipt_branch or exists_in_money_receipt):
                #         # Skip this lr_booking if CS/MR is not completed
                #         continue

                # Validation 5: Check if DeliveryStatement exists
                if DeliveryStatement.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists():
                    # Skip this lr_booking if it is already in a DeliveryStatement
                    continue

                # If all validations pass, add the lr_booking to the validated list
                validated_queryset.append(lr_booking)

            # Serialize the validated queryset data
            serializer = LRBokkingSerializer(validated_queryset, many=True)

            # Return success response with serialized data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LRPendingForPartyBillingView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extracting the optional parameter from the request body
            billing_party = request.data.get('billing_party')

            # Base queryset with fixed filters
            queryset = LR_Bokking.objects.filter(
                pay_type_id=3,  # Pay type is fixed to "3"
                is_active=True,
                flag=True
            ).order_by('-lr_no')

            # Apply `billing_party` filter if provided
            if billing_party:
                queryset = queryset.filter(billing_party_id=billing_party)

            # Filter out LR_Bokking entries that already exist in PartyBilling
            validated_queryset = [
                lr_booking for lr_booking in queryset
                if not PartyBilling.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()
            ]

            # Serialize the validated queryset data
            serializer = LRBokkingSerializer(validated_queryset, many=True)

            # Return success response with serialized data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LRPendingForVoucherReceiptView(APIView):
    def post(self, request, *args, **kwargs):
        try:            
            # Extracting the optional parameters from the request body
            pay_type = request.data.get('pay_type')

            # Base queryset with fixed filters
            queryset = LR_Bokking.objects.filter(
                pay_type_id__in=[1, 2],  # Filtering by pay type (either 1 or 2)
                is_active=True,
                flag=True
            ).order_by('-lr_no')

            # Apply optional `pay_type` filter if provided
            if pay_type:
                queryset = queryset.filter(pay_type_id=pay_type)

            # Filter out LR_Bokking entries that already exist in VoucherReceiptBranch
            validated_queryset = [
                lr_booking for lr_booking in queryset
                if not VoucherReceiptBranch.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()
            ]   

            # Serialize the validated queryset data
            serializer = LRBokkingSerializer(validated_queryset, many=True)

            # Return success response with serialized data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LRPendingForMoneyReceiptView(APIView):
    def post(self, request, *args, **kwargs):
        try:            
            # Extracting the optional parameters from the request body
            pay_type = request.data.get('pay_type')

            # Base queryset with fixed filters
            queryset = LR_Bokking.objects.filter(
                pay_type_id__in=[1, 2],  # Filtering by pay type (either 1 or 2)
                is_active=True,
                flag=True
            ).order_by('-lr_no')

            # Apply optional `pay_type` filter if provided
            if pay_type:
                queryset = queryset.filter(pay_type_id=pay_type)

            # Filter out LR_Bokking entries that already exist in MoneyReceipt
            validated_queryset = [
                lr_booking for lr_booking in queryset
                if not MoneyReceipt.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists()
            ]   

            # Serialize the validated queryset data
            serializer = LRBokkingSerializer(validated_queryset, many=True)

            # Return success response with serialized data
            response_data = {
                'msg': 'LR_Bokking retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
