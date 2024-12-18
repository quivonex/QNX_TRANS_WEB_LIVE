from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from branches.models import BranchMaster
from .models import GSTMaster,PartyBilling,VoucherReceiptType,VoucherReceiptBranch,MoneyReceipt,VoucherPaymentType,VoucherPaymentBranch,CashBook,BillingSubmission,DeductionReasonType,Deduction
from .serializers import GSTMasterSerializer,PartyBillingSerializer,VoucherReceiptTypeSerializer,VoucherReceiptBranchSerializer,MoneyReceiptSerializer,VoucherPaymentTypeSerializer,VoucherPaymentBranchSerializer,CashBookSerializer,BillingSubmissionSerializer,DeductionReasonTypeSerializer,DeductionSerializer
from django.core.exceptions import ObjectDoesNotExist
from lr_booking.models import LR_Bokking
from parties.models import PartyMaster
from django.db import transaction
from decimal import Decimal
from weasyprint import HTML, CSS
from django.http import HttpResponse
from company.models import CompanyMaster
from delivery.models import CustomerOutstanding
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from users.models import UserProfile
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from company.filters import apply_filters
from company.views import send_email_with_attachment
import os
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone

class GSTMasterCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = GSTMasterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response({
                    'status': 'success',
                    'message': 'GST Master created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Validation failed.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An error occurred.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GSTMasterRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = GSTMaster.objects.get(pk=gst_id)
            serializer = GSTMasterSerializer(instance)
            return Response({'msg': 'GST Master retrieved successfully', 'status': 'success', 'data': [serializer.data]}, status=status.HTTP_200_OK)
        except GSTMaster.DoesNotExist:
            return Response({'msg': 'GST Master not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

class GSTMasterRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all GSTMaster instances where `flag=True`, ordered by `id` in descending order
            instances = GSTMaster.objects.filter(flag=True).order_by('-id')
            serializer = GSTMasterSerializer(instances, many=True)

            # Custom response structure
            response_data = {
                'msg': 'GST records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving GST records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GSTMasterRetrieveFilteredView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve active GSTMaster records where `is_active=True` and `flag=True`, ordered by `id` in descending order
            queryset = GSTMaster.objects.filter(is_active=True, flag=True).order_by('-id')
            serializer = GSTMasterSerializer(queryset, many=True)

            # Custom response structure
            response_data = {
                'msg': 'Filtered GST records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving filtered GST records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GSTMasterUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = GSTMaster.objects.get(pk=gst_id)
            serializer = GSTMasterSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({'msg': 'GST Master updated successfully', 'status': 'success', 'data': [serializer.data]}, status=status.HTTP_200_OK)
            return Response({'msg': 'Validation failed', 'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except GSTMaster.DoesNotExist:
            return Response({'msg': 'GST Master not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

class GSTMasterDeleteView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = GSTMaster.objects.get(pk=gst_id)
            instance.flag = False
            instance.save()
            return Response({'msg': 'GST Master soft deleted successfully', 'status': 'success', 'data': {}}, status=status.HTTP_200_OK)
        except GSTMaster.DoesNotExist:
            return Response({'msg': 'GST Master not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)


class GeneratePartyBillingPDF(APIView):
    def get(self, request, delivery_no):
        # Fetch the statement details based on delivery_no
        statement = get_object_or_404(PartyBilling, bill_no=delivery_no)
        bookings = statement.lr_booking.all()

        # Fetch company details
        company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

        # Generate barcode for the delivery_no
        barcode_base64 = generate_barcode(delivery_no)

        # Get the logged-in user's name
        user_profile = UserProfile.objects.get(user=statement.created_by)
        user_name = user_profile.first_name + " "+user_profile.last_name

        # Render HTML to string
        html_string = render(request, 'party_billing/party_billing.html', {
            'company': company,
            'statement': statement,  
            'bookings': bookings,     
            'barcode_base64': barcode_base64,
            'user_name': user_name,
        }).content.decode('utf-8')

        # Define CSS
        css = CSS(string=''' 
            @page {
                size: legal;
                margin: 5mm;
            }
        ''')

        # Generate PDF
        html = HTML(string=html_string)
        pdf = html.write_pdf(stylesheets=[css])

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=Vouch_pay_branch_{delivery_no}.pdf'

        # Handle branch manager print status
        if request.user.userprofile.role == 'branch_manager':
            if statement.printed_by_branch_manager:
                return Response({"msg": "This statement has already been printed by a branch manager.", 'status': 'error'}, status=400)
            statement.printed_by_branch_manager = True
            statement.save()

        return response

class GeneratePartyBillingBillNumberViews(APIView):   
    def post(self, request, *args, **kwargs):
        print(request.data)
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
            last_booking_memo = PartyBilling.objects.filter(
                branch_name_id=branch_id,
                bill_no__startswith=prefix
            ).exclude(bill_no__isnull=True).exclude(bill_no__exact='').order_by('-bill_no').first()

            if last_booking_memo:
                last_sequence_number = int(last_booking_memo.bill_no[len(prefix):])
                new_delivery_no = f"{prefix}{str(last_sequence_number + 1).zfill(5)}"
            else:
                new_delivery_no = f"{prefix}00001"

            # On successful LR number generation
            response_data = {
                'msg': 'Bill number generated successfully',
                'status': 'success',
                'data': {
                    'bill_no': new_delivery_no
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
                'message': 'An error occurred during Bill number generation due to invalid data.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any other unexpected exceptions
            response_data = {
                'status': 'error',
                'message': 'An error occurred while generating the Bill number.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreatePartyBillingView(APIView):    
    def post(self, request, *args, **kwargs):
        data = request.data
        lr_booking_ids = data.pop('lr_booking', [])
        requested_billing_party = data.get('billing_party')

        try:
            try:
                billing_party = PartyMaster.objects.get(id=requested_billing_party)
            except PartyMaster.DoesNotExist:
                    return Response({
                        "message": f"PartyMaster with lr_no {requested_billing_party} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
            if int(billing_party.party_type_id) != 2 :                                        
                        return Response({
                            "msg": (
                                f"PartyMaster with lr_no {requested_billing_party} has not party_type 'Billing'. "                        
                            ),
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
            # Validate each LR_Bokking in the requested list
            for lr_no in lr_booking_ids:
                # Get the LR_Bokking object
                try:
                    lr_booking = LR_Bokking.objects.get(lr_no=lr_no)
                except LR_Bokking.DoesNotExist:
                    return Response({
                        "message": f"LR_Bokking with lr_no {lr_no} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 1: Ensure lr_booking is not already associated with an active PartyBilling
                if PartyBilling.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists():
                    return Response({
                        "msg": f"LR_Bokking with lr_no {lr_no} is already associated with an active PartyBilling.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 2: Check pay_type and billing_party               
                if int(lr_booking.pay_type_id) != 3 :                                        
                        return Response({
                            "msg": (
                                f"LR_Bokking with lr_no {lr_no} has not pay_type 'TBB'. "                        
                            ),
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)
                if int(lr_booking.billing_party_id) != int(requested_billing_party):    
                        return Response({
                            "msg": (
                                f"LR_Bokking with lr_no {lr_no} has billing_party does not match the requested billing_party "                        
                            ),
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)
                    

            # If all validations pass, proceed with creation
            with transaction.atomic():
                serializer = PartyBillingSerializer(data=data)
                if serializer.is_valid():
                    party_biilling = serializer.save()

                    # Add LR_Bokking entries to the ManyToMany field
                    lr_bookings = LR_Bokking.objects.filter(lr_no__in=lr_booking_ids)
                    if len(lr_bookings) != len(lr_booking_ids):
                        raise ValueError("One or more LR_Booking IDs not found.")
                    party_biilling.lr_booking.set(lr_bookings)
                    party_biilling.created_by = request.user

                    response_serializer = PartyBillingSerializer(party_biilling)
                    return Response({
                        "message": "Party Billing Statement created successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_201_CREATED)

                return Response({
                    "message": "Failed to create Party Billing",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "message": "An error occurred while creating Party Billing",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class PartyBillingRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        standard_rate_id = request.data.get('id')

        # Check if 'id' is provided
        if not standard_rate_id:
            return Response({
                'message': 'Party Billing ID is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the StandardRate instance
            standard_rate = PartyBilling.objects.get(id=standard_rate_id)
        except PartyBilling.DoesNotExist:
            return Response({
                'message': 'Party Billing not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = PartyBillingSerializer(standard_rate)

        # Return the data with success status
        return Response({
            'message': 'Party Billing retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)

class PartyBillingRetrieveViewBybill_no(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        standard_rate_id = request.data.get('bill_no')

        # Check if 'id' is provided
        if not standard_rate_id:
            return Response({
                'message': 'Party Billing bill_no is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the StandardRate instance
            standard_rate = PartyBilling.objects.get(bill_no=standard_rate_id)
        except PartyBilling.DoesNotExist:
            return Response({
                'message': 'Party Billing not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = PartyBillingSerializer(standard_rate)

        # Return the data with success status
        return Response({
            'message': 'Party Billing retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
 
class PartyBillingRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            branch_id = request.data.get("branch_id")
            user_profile = UserProfile.objects.get(user=request.user)            
            allowed_branches = user_profile.branches.all()

            if not branch_id:
                return Response({
                    "status": "error",
                    "message": "Branch ID is required."
                }, status=status.HTTP_400_BAD_REQUEST)


            # Retrieve all items from the database
            items = PartyBilling.objects.filter(
                flag=True
                ).filter(
                Q(branch_name__in=allowed_branches) 
                ).filter(
                Q(branch_name_id=branch_id)
                ).order_by('-id')

            # Serialize the items data
            serializer = PartyBillingSerializer(items, many=True)

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
    
class PartyBillingRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter the queryset for active StandardRate instances
            queryset = PartyBilling.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = PartyBillingSerializer(queryset, many=True)

            # Prepare the response data
            response_data = {
                'msg': 'Party Billing retrieved successfully',
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

class PartyBillingRetrieveVoucherReceiptView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter the queryset for active StandardRate instances
            queryset = PartyBilling.objects.filter(is_active=True,flag=True).order_by('-id')
            validated_queryset = [
                party_billing for party_billing in queryset
                if not  VoucherReceiptBranch.objects.filter(
                    party_billing=party_billing,
                    is_active=True,
                    flag=True
                ).exists()
            ]   
            serializer = PartyBillingSerializer(validated_queryset, many=True)

            # Prepare the response data
            response_data = {
                'msg': 'Party Billing retrieved successfully',
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

class PartyBillingRetrieveMoneyReceiptView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter the queryset for active StandardRate instances
            queryset = PartyBilling.objects.filter(is_active=True,flag=True).order_by('-id')
            validated_queryset = [
                party_billing for party_billing in queryset
                if not  MoneyReceipt.objects.filter(
                    party_billing=party_billing,
                    is_active=True,
                    flag=True
                ).exists()
            ]   
            serializer = PartyBillingSerializer(validated_queryset, many=True)

            # Prepare the response data
            response_data = {
                'msg': 'Party Billing retrieved successfully',
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

class PartyBillingRetrieveBillingSubmissionView(APIView):
    def post(self, request, *args, **kwargs):
        print("request",request.data)
        try:
            # Expecting 'id' in the POST data
            branch_name = request.data.get('branch_name')
            print("party billing", branch_name)
            # Check if 'id' is provided
            if not branch_name:
                return Response({
                    'message': 'Party Billing branch_name is required',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            # Filter the queryset for active StandardRate instances
            queryset = PartyBilling.objects.filter(is_active=True,flag=True,branch_name_id=branch_name).order_by('-id')
            validated_queryset = [
                party_billing for party_billing in queryset
                if not  BillingSubmission.objects.filter(
                    bill_no=party_billing,
                    is_active=True,
                    flag=True
                ).exists()
            ]   
            serializer = PartyBillingSerializer(validated_queryset, many=True)

            # Prepare the response data
            response_data = {
                'msg': 'Party Billing retrieved successfully',
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

class PartyBillingFilterView(APIView): 
    def post(self, request, *args, **kwargs):        
        try:       
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(PartyBilling, filters)

            # Serialize the filtered data
            serializer = PartyBillingSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class UpdatePartyBillingView(APIView):    
    def post(self, request, *args, **kwargs):
        data = request.data
        delivery_statement_id = data.get('id')  # Retrieve the ID of the PartyBilling to update
        lr_booking_ids = data.pop('lr_booking', [])
        requested_billing_party = data.get('billing_party')

        if not delivery_statement_id:
            return Response({
                "message": "ID of the PartyBilling record is required.",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            try:
                billing_party = PartyMaster.objects.get(id=requested_billing_party)
            except PartyMaster.DoesNotExist:
                    return Response({
                        "message": f"PartyMaster with lr_no {requested_billing_party} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
            if int(billing_party.party_type_id) != 2 :                                        
                        return Response({
                            "msg": (
                                f"PartyMaster with lr_no {requested_billing_party} has not Party_Type 'Billing'. "                        
                            ),
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            # Fetch the PartyBilling instance
            try:
                party_billing = PartyBilling.objects.get(id=delivery_statement_id, is_active=True, flag=True)
            except PartyBilling.DoesNotExist:
                return Response({
                    "message": f"PartyBilling with id {delivery_statement_id} does not exist or is inactive.",
                    "status": "error"
                }, status=status.HTTP_404_NOT_FOUND)

            # Validate each LR_Bokking in the requested list
            for lr_no in lr_booking_ids:
                # Get the LR_Bokking object
                try:
                    lr_booking = LR_Bokking.objects.get(lr_no=lr_no)
                except LR_Bokking.DoesNotExist:
                    return Response({
                        "message": f"LR_Bokking with lr_no {lr_no} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 1: Ensure lr_booking is not already associated with another active PartyBilling
                if PartyBilling.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exclude(id=delivery_statement_id).exists():
                    return Response({
                        "msg": f"LR_Bokking with lr_no {lr_no} is already associated with another active PartyBilling.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 2: Check pay_type and billing_party               
                if int(lr_booking.pay_type_id) != 3 :                                        
                        return Response({
                            "msg": (
                                f"LR_Bokking with lr_no {lr_no} has not pay_type 'TBB'. "                        
                            ),
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)
                if int(lr_booking.billing_party_id) != int(requested_billing_party):    
                        return Response({
                            "msg": (
                                f"LR_Bokking with lr_no {lr_no} has billing_party does not match the requested billing_party "                        
                            ),
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)

            # If all validations pass, proceed with the update
            with transaction.atomic():
                serializer = PartyBillingSerializer(party_billing, data=data, partial=True)
                if serializer.is_valid():
                    updated_party_billing = serializer.save(updated_by=request.user)

                    # Update LR_Bokking entries in the ManyToMany field
                    lr_bookings = LR_Bokking.objects.filter(lr_no__in=lr_booking_ids)
                    if len(lr_bookings) != len(lr_booking_ids):
                        raise ValueError("One or more LR_Booking IDs not found.")
                    updated_party_billing.lr_booking.set(lr_bookings)

                    response_serializer = PartyBillingSerializer(updated_party_billing)
                    return Response({
                        "message": "Party Billing Statement updated successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_200_OK)

                return Response({
                    "message": "Failed to update Party Billing",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "message": "An error occurred while updating Party Billing",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class PartyBillingSoftDeleteAPIView(APIView):
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
            instance = PartyBilling.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'Party Billing deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except PartyBilling.DoesNotExist:
            return Response({
                'msg': 'StandardRate not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class PartyBillingPermanentDeleteAPIView(APIView):
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
            instance = PartyBilling.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'Party Billing permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except PartyBilling.DoesNotExist:
            return Response({
                'msg': 'StandardRate not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)


class VoucherReceiptTypeCreateView(APIView):    
    def post(self, request, *args, **kwargs):
        try:
            serializer = VoucherReceiptTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response({
                    'status': 'success',
                    'message': 'Voucher Receipt Type created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Validation failed.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An error occurred.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoucherReceiptTypeRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = VoucherReceiptType.objects.get(pk=gst_id)
            serializer = VoucherReceiptTypeSerializer(instance)
            return Response({'msg': 'Voucher Receipt Type retrieved successfully', 'status': 'success', 'data': [serializer.data]}, status=status.HTTP_200_OK)
        except VoucherReceiptType.DoesNotExist:
            return Response({'msg': 'Voucher Receipt Type not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

class VoucherReceiptTypeRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all GSTMaster instances where `flag=True`, ordered by `id` in descending order
            instances = VoucherReceiptType.objects.filter(flag=True).order_by('-id')
            serializer = VoucherReceiptTypeSerializer(instances, many=True)

            # Custom response structure
            response_data = {
                'msg': 'Voucher Receipt Type records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving Voucher Receipt Type records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoucherReceiptTypeRetrieveFilteredView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve active GSTMaster records where `is_active=True` and `flag=True`, ordered by `id` in descending order
            queryset = VoucherReceiptType.objects.filter(is_active=True, flag=True).order_by('-id')
            serializer = VoucherReceiptTypeSerializer(queryset, many=True)

            # Custom response structure
            response_data = {
                'msg': 'Filtered Voucher Receipt Type records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving filtered Voucher Receipt Type records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoucherReceiptTypeRetrieveMoneyReceiptView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve active GSTMaster records where `is_active=True` and `flag=True`, ordered by `id` in descending order
            queryset = VoucherReceiptType.objects.filter(is_active=True, flag=True).exclude(id=3).order_by('-id')
            serializer = VoucherReceiptTypeSerializer(queryset, many=True)

            # Custom response structure
            response_data = {
                'msg': 'Filtered Voucher Receipt Type records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving filtered Voucher Receipt Type records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoucherReceiptTypeUpdateView(APIView):
    def post(self, request, *args, **kwargs):        
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = VoucherReceiptType.objects.get(pk=gst_id)
            serializer = VoucherReceiptTypeSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({'msg': 'Voucher Receipt Type updated successfully', 'status': 'success', 'data': [serializer.data]}, status=status.HTTP_200_OK)
            return Response({'msg': 'Validation failed', 'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except VoucherReceiptType.DoesNotExist:
            return Response({'msg': 'Voucher Receipt Type not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

class VoucherReceiptTypeDeleteView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = VoucherReceiptType.objects.get(pk=gst_id)
            instance.flag = False
            instance.save()
            return Response({'msg': 'Voucher Receipt Type soft deleted successfully', 'status': 'success', 'data': {}}, status=status.HTTP_200_OK)
        except VoucherReceiptType.DoesNotExist:
            return Response({'msg': 'Voucher Receipt Type not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)



def generate_barcode(memo_no):
    # Convert memo_no to string as the barcode library expects a string
    memo_no_str = str(memo_no)

    # Create an in-memory bytes buffer to store the barcode image
    buffer = BytesIO()

    # Generate the barcode using CODE128 format without text below
    CODE128 = barcode.get_barcode_class('code128')
    barcode_image = CODE128(memo_no_str, writer=ImageWriter())

    # Disable text rendering (don't show the memo_no below the barcode)
    barcode_image.write(buffer, {'write_text': False})

    # Encode the barcode image to base64 so that it can be embedded in HTML
    buffer.seek(0)
    barcode_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return barcode_base64

class GenerateVoucherReceiptBranchPDF(APIView):
    def get(self, request, delivery_no):
        # Fetch the statement details based on delivery_no
        statement = get_object_or_404(VoucherReceiptBranch, id=delivery_no)
        bookings = statement.lr_booking.all()
        parties = statement.party_billing.all()

        # Fetch company details
        company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

        # Generate barcode for the delivery_no
        barcode_base64 = generate_barcode(delivery_no)

        # Get the logged-in user's name
        user_profile = UserProfile.objects.get(user=statement.created_by)
        user_name = user_profile.first_name + " "+user_profile.last_name

        # Render HTML to string
        html_string = render(request, 'Vouch_rpt_branch/Vouch_rpt_branch.html', {
            'company': company,
            'statement': statement,
            'bookings': bookings,
            'parties':parties,
            'barcode_base64': barcode_base64,
            'user_name': user_name,
        }).content.decode('utf-8')

        # Define CSS
        css = CSS(string=''' 
            @page {
                size: legal;
                margin: 5mm;
            }
        ''')

        # Generate PDF
        html = HTML(string=html_string)
        pdf = html.write_pdf(stylesheets=[css])

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=Vouch_rpt_branch_{delivery_no}.pdf'

        # Handle branch manager print status
        if request.user.userprofile.role == 'branch_manager':
            if statement.printed_by_branch_manager:
                return Response({"msg": "This statement has already been printed by a branch manager.", 'status': 'error'}, status=400)
            statement.printed_by_branch_manager = True
            statement.save()

        return response

class CreateVoucherReceiptBranchView(APIView):    
    def post(self, request, *args, **kwargs):
        data = request.data
        lr_booking_ids = data.pop('lr_booking', [])
        party_billing_ids = data.get('party_billing', [])
        receipt_type = data.get('receipt_type')
        try:
            # Contra Entry Validation
            if receipt_type == 3:  # If receipt_type is contra
                if lr_booking_ids or party_billing_ids:
                    return Response({
                        "msg": "For Contra entry, there is no need for any lr_booking or party_billing. Please remove all of these.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if not data.get('to_branch') or not data.get('to_branch_amt'):
                        return Response({
                            "msg": "Fields 'to_branch' and 'to_branch_amt' are mandatory when receipt_type is contra .",
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)
            else:  # If receipt_type is not contra
                if not lr_booking_ids and not party_billing_ids:
                    return Response({
                        "msg": "Your receipt_type is not contra, but no lr_booking or party_billing records were provided.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Check if lr_booking or party_billing exists, then clear to_branch and to_branch_amt
            if lr_booking_ids or party_billing_ids:               
                data['to_branch'] = None
                data['to_branch_amt'] = None  

            # Validate `date` presence
            if not data.get('date'):
                return Response({
                    "msg": "The 'date' field is mandatory.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            date = data.get('date')              

            # Validate each LR_Bokking in the requested list
            for lr_no in lr_booking_ids:
                # Get the LR_Bokking object
                try:
                    lr_booking = LR_Bokking.objects.get(lr_no=lr_no)
                except LR_Bokking.DoesNotExist:
                    return Response({
                        "message": f"LR_Bokking with lr_no {lr_no} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validation 1: Ensure lr_booking is not already associated with an active PartyBilling
                if VoucherReceiptBranch.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists():
                    return Response({
                        "msg": f"LR_Bokking with lr_no {lr_no} is already associated with an active Voucher Receipt Branch.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validation 2: Check pay_type               
                if int(lr_booking.pay_type_id) != 1 and int(lr_booking.pay_type_id) != 2:
                    return Response({
                        "msg": f"LR_Bokking with lr_no {lr_no} has not pay_type 'Paid' or 'TOPAY'.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                            
            # Validate each party_billing in the requested list
            for party_bill in party_billing_ids:
                # Get the LR_Bokking object
                try:
                    party_billing = PartyBilling.objects.get(id=party_bill)
                except PartyBilling.DoesNotExist:
                    return Response({
                        "message": f"party_billing with lr_no {party_bill} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)                
                
                # Validation 1: Ensure party_billing is not already associated with an active PartyBilling                
                if VoucherReceiptBranch.objects.filter(
                    party_billing=party_billing,
                    is_active=True,
                    flag=True
                ).exists():
                    return Response({
                        "msg": f"Party_billing with lr_no {party_bill} is already associated with an active Voucher Receipt Branch.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                
                
            # If all validations pass, proceed with creation
            with transaction.atomic():
                serializer = VoucherReceiptBranchSerializer(data=data)
                if serializer.is_valid():
                    voucher_receipt = serializer.save()

                    # Add LR_Bokking entries to the ManyToMany field
                    lr_bookings = LR_Bokking.objects.filter(lr_no__in=lr_booking_ids)
                    if len(lr_bookings) != len(lr_booking_ids):
                        raise ValueError("One or more LR_Booking IDs not found.")
                    voucher_receipt.lr_booking.set(lr_bookings)

                    # Add LR_Bokking entries to the ManyToMany field
                    party_billings = PartyBilling.objects.filter(id__in=party_billing_ids)
                    if len(party_billings) != len(party_billing_ids):
                        raise ValueError("One or more party_billings IDs not found.")
                    voucher_receipt.party_billing.set(party_billings)

                    voucher_receipt.created_by = request.user

                    # Process the LR_Booking records and update CustomerOutstanding
                    for lr_no in lr_booking_ids:
                        try:
                            # Find the corresponding CustomerOutstanding record
                            customer_outstanding = CustomerOutstanding.objects.filter(lr_booking__lr_no=lr_no)
                            for outstanding in customer_outstanding:
                                # Remove the lr_booking from this CustomerOutstanding
                                outstanding.lr_booking.remove(lr_no)

                                # Update the last_credit_date
                                outstanding.last_credit_date = timezone.now().date()
                                outstanding.save()

                                # If no more lr_booking objects exist for this record, set last_credit_date to null
                                if not outstanding.lr_booking.exists():
                                    outstanding.last_credit_date = None
                                    outstanding.save()

                        except CustomerOutstanding.DoesNotExist:
                            pass  # Handle any case where the CustomerOutstanding record doesn't exist                        
                    
                    # Determine branch_id and amount for credit_operation
                    if (data.get('to_branch') != None):
                        branch_id = data.get('to_branch')                     
                        amount = Decimal(data.get('to_branch_amt'))                     
                    else:                        
                        branch_id =data.get('branch_name')                     
                        amount = Decimal(data.get('totla_amt'))              

                    # Perform credit operation
                    cash_book = CashBook()
                    cash_book.credit_operation(branch_id=branch_id, voucher_id=voucher_receipt.id, date=date, amount=amount)

                    # Additional Logic: Create VoucherPaymentBranch if `to_branch` is present
                    if (data.get('to_branch') != None):
                        # Generate Voucher Number
                        branch_name = data.get('branch_name')
                        branch = BranchMaster.objects.get(id=branch_name, is_active=True, flag=True)
                        branch_code = branch.branch_code
                        prefix = f"{branch_code}"
                        last_voucher = VoucherPaymentBranch.objects.filter(
                            branch_name_id=branch_name,
                            voucher_no__startswith=prefix
                        ).exclude(voucher_no__isnull=True).exclude(voucher_no__exact='').order_by('-voucher_no').first()

                        if last_voucher:
                            last_sequence_number = int(last_voucher.voucher_no[len(prefix):])
                            new_voucher_no = f"{prefix}{str(last_sequence_number + 1).zfill(5)}"
                        else:
                            new_voucher_no = f"{prefix}00001"

                        # Create VoucherPaymentBranch Object
                        remarks = f"Send Payment to {data['to_branch']} branch"
                        voucher_payment_branch = VoucherPaymentBranch.objects.create(
                            date=date,
                            branch_name_id=branch_name,
                            voucher_no=new_voucher_no,
                            amount=Decimal(data.get('to_branch_amt')),
                            created_by=request.user,
                            remarks=remarks
                        )

                        # Perform Debit Operation
                        cash_book.debit_operation(
                            branch_id=branch_name,
                            date=date,
                            amount=Decimal(data.get('to_branch_amt')),
                            payment_id=voucher_payment_branch.id
                        )

                    response_serializer = VoucherReceiptBranchSerializer(voucher_receipt)
                    return Response({
                        "message": "Voucher Receipt Branch created successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_201_CREATED)

                return Response({
                    "message": "Failed to create Voucher Receipt Branch",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "message": "An error occurred while creating Voucher Receipt Branch",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class VoucherReceiptBranchRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        standard_rate_id = request.data.get('id')

        # Check if 'id' is provided
        if not standard_rate_id:
            return Response({
                'message': 'Voucher Receipt Branch ID is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the StandardRate instance
            standard_rate = VoucherReceiptBranch.objects.get(id=standard_rate_id)
        except VoucherReceiptBranch.DoesNotExist:
            return Response({
                'message': 'Voucher Receipt Branch not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = VoucherReceiptBranchSerializer(standard_rate)

        # Return the data with success status
        return Response({
            'message': 'Voucher Receipt Branch retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    
class VoucherReceiptBranchRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            branch_id = request.data.get("branch_id")
            user_profile = UserProfile.objects.get(user=request.user)            
            allowed_branches = user_profile.branches.all()

            if not branch_id:
                return Response({
                    "status": "error",
                    "message": "Branch ID is required."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Retrieve all items from the database
            items = VoucherReceiptBranch.objects.filter(
                flag=True
                ).filter(
                Q(branch_name__in=allowed_branches)
                ).filter(
                Q(branch_name_id=branch_id)
                ).order_by('-id')

            # Serialize the items data
            serializer = VoucherReceiptBranchSerializer(items, many=True)

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
    
class VoucherReceiptBranchRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter the queryset for active StandardRate instances
            queryset = VoucherReceiptBranch.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = VoucherReceiptBranchSerializer(queryset, many=True)

            # Prepare the response data
            response_data = {
                'msg': 'Voucher Receipt Branch retrieved successfully',
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

class VoucherReceiptBranchFilterView(APIView): 
    def post(self, request, *args, **kwargs):
        try:
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(VoucherReceiptBranch, filters)

            # Serialize the filtered data
            serializer = VoucherReceiptBranchSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class UpdateVoucherReceiptBranchView(APIView):        
    def post(self, request, *args, **kwargs):
        data = request.data
        delivery_statement_id = data.get('id')  
        lr_booking_ids = data.pop('lr_booking', [])
        party_billing_ids = data.get('party_billing', [])
        receipt_type = data.get('receipt_type')

        if not delivery_statement_id:
            return Response({
                "message": "ID of the Voucher Receipt Branch record is required.",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the PartyBilling instance
            try:
                voucher_receipt = VoucherReceiptBranch.objects.get(id=delivery_statement_id, is_active=True, flag=True)
            except VoucherReceiptBranch.DoesNotExist:
                return Response({
                    "message": f"Voucher Receipt Branch with id {delivery_statement_id} does not exist or is inactive.",
                    "status": "error"
                }, status=status.HTTP_404_NOT_FOUND)

            # Contra Entry Validation
            if receipt_type == 3:  # If receipt_type is contra
                if lr_booking_ids or party_billing_ids:
                    return Response({
                        "msg": "For Contra entry, there is no need for any lr_booking or party_billing. Please remove all of these.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if not data.get('to_branch') or not data.get('to_branch_amt'):
                        return Response({
                            "msg": "Fields 'to_branch' and 'to_branch_amt' are mandatory when receipt_type is contra .",
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)
            else:  # If receipt_type is not contra
                if not lr_booking_ids and not party_billing_ids:
                    return Response({
                        "msg": "Your receipt_type is not contra, but no lr_booking or party_billing records were provided.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Check if lr_booking or party_billing exists, then clear to_branch and to_branch_amt
            if lr_booking_ids or party_billing_ids:               
                data['to_branch'] = None
                data['to_branch_amt'] = None     

            # Validate `date` presence
            if not data.get('date'):
                return Response({
                    "msg": "The 'date' field is mandatory.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            date = data.get('date')      

            # Validate each LR_Bokking in the requested list
            for lr_no in lr_booking_ids:
                # Get the LR_Bokking object
                try:
                    lr_booking = LR_Bokking.objects.get(lr_no=lr_no)
                except LR_Bokking.DoesNotExist:
                    return Response({
                        "message": f"LR_Bokking with lr_no {lr_no} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 1: Ensure lr_booking is not already associated with another active VoucherReceiptBranch
                if VoucherReceiptBranch.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exclude(id=delivery_statement_id).exists():
                    return Response({
                        "msg": f"LR_Bokking with lr_no {lr_no} is already associated with another active VoucherReceiptBranch.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 2: Check pay_type               
                if int(lr_booking.pay_type_id) != 1 and int(lr_booking.pay_type_id) != 2:
                    return Response({
                        "msg": f"LR_Bokking with lr_no {lr_no} has not pay_type 'Paid' or 'TOPAY'.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
             # Validate each party_billing in the requested list
            for party_bill in party_billing_ids:
                # Get the LR_Bokking object
                try:
                    party_billing = PartyBilling.objects.get(id=party_bill)
                except PartyBilling.DoesNotExist:
                    return Response({
                        "message": f"party_billing with lr_no {party_bill} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)                
                
                # Validation 1: Ensure party_billing is not already associated with an active PartyBilling                
                if VoucherReceiptBranch.objects.filter(
                    party_billing=party_billing,
                    is_active=True,
                    flag=True
                ).exclude(id=delivery_statement_id).exists():
                    return Response({
                        "msg": f"Party_billing with lr_no {party_bill} is already associated with an active Voucher Receipt Branch.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)


            # If all validations pass, proceed with the update
            with transaction.atomic():
                # Determine branch_id and amount for credit_operation
                if (data.get('to_branch') != None):
                    branch_id = data.get('to_branch')                     
                    amount = Decimal(data.get('to_branch_amt'))                     
                else:                        
                    branch_id =data.get('branch_name')                     
                    amount = Decimal(data.get('totla_amt')) 

                # Validate `CashBook` Record
                cash_book = CashBook.objects.filter(branch_name_id=branch_id, date=date).first()
                if not cash_book:
                    # Check for last record by branch
                    cash_book = CashBook.objects.filter(branch_name_id=branch_id, date__lt=date).order_by('-date').first()
                    if not cash_book:
                        return Response({
                            "message": "Please check the provided date is Today's date, Beacause No CashBook record found for the branch with match or below the date, to avoid bad effect on cash book this update is restricated.",
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)

                # Check for subsequent entries
                subsequent_entries = CashBook.objects.filter(branch_name_id=branch_id, date__gt=cash_book.date).exists()

                if subsequent_entries:
                    # Handle `to_branch` validation
                    if (data.get('to_branch') != None):
                        if amount != voucher_receipt.to_branch_amt:
                            return Response({
                                "message": "You cannot update `to_branch_amt` Because this date closing balance is present inside next date opening balance.",
                                "status": "error"
                            }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle `totla_amt` validation
                        if amount != voucher_receipt.totla_amt:
                            return Response({
                                "message": "You cannot update `totla_amt` Because this date closing balance is present inside next date opening balance.",
                                "status": "error"
                            }, status=status.HTTP_400_BAD_REQUEST)

                else:
                    # Adjust closing balance for last entry
                    if (data.get('to_branch') != None):
                        difference = amount - voucher_receipt.to_branch_amt
                    else:
                        difference = amount - voucher_receipt.totla_amt

                    cash_book.closing_balance += abs(difference)
                    cash_book.save()

                if (difference != 0):
                    if (data.get('to_branch') != None):
                        # Validate `CashBook` Record
                        cash_book_2 = CashBook.objects.filter(branch_name_id=data.get('branch_name'), date=cash_book.date).first()
                        if not cash_book_2:
                                raise ValueError(f"CashBook record not found for find debit record of sender branch.")
                        # Check for subsequent entries
                        subsequent_entries_2 = CashBook.objects.filter(branch_name_id=data.get('branch_name'), date__gt=cash_book_2.date).exists()
                        if subsequent_entries_2:
                            raise ValueError(f"We can not update this record because based on the Voucher payent debit entry there is next day cashbook present.")
                        print(voucher_receipt.to_branch_amt)
                        voucher_payment = cash_book_2.debit.filter(
                            amount=voucher_receipt.to_branch_amt,
                            remarks=f"Send Payment to {data['to_branch']} branch"
                        ).first()

                        # If no matching record is found, raise an error
                        if not voucher_payment:
                            raise ValueError(f"VoucherPaymentBranch record not found to debit amount.")
                    
                        # Update the `VoucherPaymentBranch` object with the new amount
                        voucher_payment.amount = amount
                        voucher_payment.save()

                        # Calculate the difference between the found `VoucherPaymentBranch` amount and the `amount`
                        difference_2 = voucher_receipt.to_branch_amt - voucher_payment.amount
                        cash_book_2.closing_balance += abs(difference_2)
                        cash_book_2.save()

                serializer = VoucherReceiptBranchSerializer(voucher_receipt, data=data, partial=True)
                if serializer.is_valid():
                    updated_voucher_receipt = serializer.save(updated_by=request.user)

                    # Update LR_Bokking entries in the ManyToMany field
                    if lr_booking_ids:
                        lr_bookings = LR_Bokking.objects.filter(lr_no__in=lr_booking_ids)
                        if len(lr_bookings) != len(lr_booking_ids):
                            raise ValueError("One or more LR_Booking IDs not found.")
                        updated_voucher_receipt.lr_booking.set(lr_bookings)
                    else:
                        # Clear all related LR_Bokking if list is empty
                        updated_voucher_receipt.lr_booking.clear()

                    # Add LR_Bokking entries to the ManyToMany field
                    if party_billing_ids:
                        party_billings = PartyBilling.objects.filter(id__in=party_billing_ids)
                        if len(party_billings) != len(party_billing_ids):
                            raise ValueError("One or more party_billings IDs not found.")
                        updated_voucher_receipt.party_billing.set(party_billings)
                    else:
                        # Clear all related PartyBilling if list is empty
                        updated_voucher_receipt.party_billing.clear()


                    response_serializer = VoucherReceiptBranchSerializer(updated_voucher_receipt)
                    return Response({
                        "message": "Voucher Receipt Branch updated successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_200_OK)

                return Response({
                    "message": "Failed to update Voucher Receipt Branch",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "message": "An error occurred while updating Voucher Receipt Branch",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class VoucherReceiptBranchSoftDeleteAPIView(APIView):
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
            instance = VoucherReceiptBranch.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'Voucher Receipt Branch deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except VoucherReceiptBranch.DoesNotExist:
            return Response({
                'msg': 'StandardRate not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class VoucherReceiptBranchPermanentDeleteAPIView(APIView):
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
            instance = VoucherReceiptBranch.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'Voucher Receipt Branch permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except VoucherReceiptBranch.DoesNotExist:
            return Response({
                'msg': 'Voucher Receipt Branch not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)


class GenerateMoneyReceiptPDF(APIView):
    def get(self, request, delivery_no):
        # Fetch the statement details based on delivery_no
        statement = get_object_or_404(MoneyReceipt, id=delivery_no)
        bookings = statement.lr_booking.all()
        parties = statement.party_billing.all()

        # Fetch company details
        company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

        # Generate barcode for the delivery_no
        barcode_base64 = generate_barcode(delivery_no)

        # Get the logged-in user's name
        user_profile = UserProfile.objects.get(user=statement.created_by)
        user_name = user_profile.first_name + " "+user_profile.last_name

        # Render HTML to string
        html_string = render(request, 'money_rpt/money_rpt.html', {
            'company': company,
            'statement': statement,
            'bookings': bookings,
            'parties':parties,
            'barcode_base64': barcode_base64,
            'user_name': user_name,
        }).content.decode('utf-8')

        # Define CSS
        css = CSS(string=''' 
            @page {
                size: legal;
                margin: 5mm;
            }
        ''')

        # Generate PDF
        html = HTML(string=html_string)
        pdf = html.write_pdf(stylesheets=[css])

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=money_rpt_{delivery_no}.pdf'

        # Handle branch manager print status
        if request.user.userprofile.role == 'branch_manager':
            if statement.printed_by_branch_manager:
                return Response({"msg": "This statement has already been printed by a branch manager.", 'status': 'error'}, status=400)
            statement.printed_by_branch_manager = True
            statement.save()

        return response

class CreateMoneyReceiptView(APIView):    
    def post(self, request, *args, **kwargs):
        data = request.data
        lr_booking_ids = data.pop('lr_booking', [])
        party_billing_ids = data.get('party_billing', [])
        pay_type = data.get('pay_type', None)

        try:
            # Store unique PartyMaster objects
            party_masters = set()

            # Validate each LR_Bokking in the requested list
            for lr_no in lr_booking_ids:
                # Get the LR_Bokking object
                try:
                    lr_booking = LR_Bokking.objects.get(lr_no=lr_no)
                except LR_Bokking.DoesNotExist:
                    return Response({
                        "message": f"LR_Bokking with lr_no {lr_no} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validation 1: Ensure lr_booking is not already associated with an active MoneyReceipt
                if MoneyReceipt.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exists():
                    return Response({
                        "message": f"LR_Bokking with lr_no {lr_no} is already associated with an active Money Receipt.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validation 2: Check pay_type               
                if int(lr_booking.pay_type_id) != 1 and int(lr_booking.pay_type_id) != 2:
                    return Response({
                        "message": f"LR_Bokking with lr_no {lr_no} has not pay_type 'Paid' or 'TOPAY'.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Add billing_party to the set
                if lr_booking.billing_party:
                    party_masters.add(lr_booking.billing_party)
                            
            # Validate each party_billing in the requested list
            for party_bill in party_billing_ids:
                # Get the LR_Bokking object
                try:
                    party_billing = PartyBilling.objects.get(id=party_bill)
                except PartyBilling.DoesNotExist:
                    return Response({
                        "message": f"party_billing with id {party_bill} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)                
                
                # Validation 1: Ensure party_billing is not already associated with an active MoneyReceipt                
                if MoneyReceipt.objects.filter(
                    party_billing=party_billing,
                    is_active=True,
                    flag=True
                ).exists():
                    return Response({
                        "message": f"Party_billing with lr_no {party_bill} is already associated with an active MoneyReceipt.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Add billing_party to the set
                if party_billing.billing_party:
                    party_masters.add(party_billing.billing_party)

            # Ensure all billing_party objects are the same
            if len(party_masters) > 1:
                return Response({
                    "message": "All lr_booking and party_billing entries must have the same billing_party.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)                

            # Validation for pay_type-specific fields and ensuring irrelevant fields are blank/null
            if pay_type == "UPI":
                if not data.get("utr_no"):
                    return Response({
                        "message": "For 'UPI' pay_type, 'utr_no' is required.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Ensure unrelated fields are null/blank
                data["rtgs_no"] = None
                data["bank_name"] = None
                data["check_no"] = None
                data["check_date"] = None

            elif pay_type == "RTGS/NFT":
                if not data.get("rtgs_no"):
                    return Response({
                        "message": "For 'RTGS/NFT' pay_type, 'rtgs_no' is required.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Ensure unrelated fields are null/blank
                data["utr_no"] = None
                data["bank_name"] = None
                data["check_no"] = None
                data["check_date"] = None

            elif pay_type == "CHECK":
                if not data.get("bank_name"):
                    return Response({
                        "message": "For 'CHECK' pay_type, 'bank_name' is required.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                if not data.get("check_no"):
                    return Response({
                        "message": "For 'CHECK' pay_type, 'check_no' is required.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                if not data.get("check_date"):
                    return Response({
                        "message": "For 'CHECK' pay_type, 'check_date' is required.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Ensure unrelated fields are null/blank
                data["utr_no"] = None
                data["rtgs_no"] = None

            else:
                return Response({
                    "message": "Invalid pay_type provided.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            # If all validations pass, proceed with creation
            with transaction.atomic():

                # Process the LR_Booking records and update CustomerOutstanding
                for lr_no in lr_booking_ids:
                    try:
                        # Find the corresponding CustomerOutstanding record
                        customer_outstanding = CustomerOutstanding.objects.filter(lr_booking__lr_no=lr_no)
                        for outstanding in customer_outstanding:
                            # Remove the lr_booking from this CustomerOutstanding
                            outstanding.lr_booking.remove(lr_no)

                            # Update the last_credit_date
                            outstanding.last_credit_date = timezone.now().date()
                            outstanding.save()

                            # If no more lr_booking objects exist for this record, set last_credit_date to null
                            if not outstanding.lr_booking.exists():
                                outstanding.last_credit_date = None
                                outstanding.save()

                    except CustomerOutstanding.DoesNotExist:
                        pass  # Handle any case where the CustomerOutstanding record doesn't exist

                serializer = MoneyReceiptSerializer(data=data)
                if serializer.is_valid():
                    money_receipt = serializer.save()

                    # Add LR_Bokking entries to the ManyToMany field
                    lr_bookings = LR_Bokking.objects.filter(lr_no__in=lr_booking_ids)
                    if len(lr_bookings) != len(lr_booking_ids):
                        raise ValueError("One or more LR_Booking IDs not found.")
                    money_receipt.lr_booking.set(lr_bookings)

                    # Add LR_Bokking entries to the ManyToMany field
                    party_billings = PartyBilling.objects.filter(id__in=party_billing_ids)
                    if len(party_billings) != len(party_billing_ids):
                        raise ValueError("One or more party_billings IDs not found.")
                    money_receipt.party_billing.set(party_billings)
                    money_receipt.created_by = request.user

                    response_serializer = MoneyReceiptSerializer(money_receipt)
                    return Response({
                        "message": "Money Receipt created successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_201_CREATED)

                return Response({
                    "message": "Failed to create Money Receipt",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "message": "An error occurred while creating Money Receipt",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class MoneyReceiptRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        standard_rate_id = request.data.get('id')

        # Check if 'id' is provided
        if not standard_rate_id:
            return Response({
                'message': 'Money Receipt ID is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the StandardRate instance
            standard_rate = MoneyReceipt.objects.get(id=standard_rate_id)
        except MoneyReceipt.DoesNotExist:
            return Response({
                'message': 'Money Receipt not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = MoneyReceiptSerializer(standard_rate)

        # Return the data with success status
        return Response({
            'message': 'Money Receipt retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    
class MoneyReceiptRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            branch_id = request.data.get("branch_id")
            user_profile = UserProfile.objects.get(user=request.user)            
            allowed_branches = user_profile.branches.all()
            if not branch_id:
                return Response({
                    "status": "error",
                    "message": "Branch ID is required."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Retrieve all items from the database
            items = MoneyReceipt.objects.filter(
                flag=True
                ).filter(
                Q(branch_name__in=allowed_branches)
                ).filter(
                Q(branch_name_id=branch_id)
                ).order_by('-id')

            # Serialize the items data
            serializer = MoneyReceiptSerializer(items, many=True)

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
    
class MoneyReceiptRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter the queryset for active StandardRate instances
            queryset = MoneyReceipt.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = MoneyReceiptSerializer(queryset, many=True)

            # Prepare the response data
            response_data = {
                'msg': 'MoneyReceipt retrieved successfully',
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

class MoneyReceiptFilterView(APIView): 
    def post(self, request, *args, **kwargs):
        try:
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(MoneyReceipt, filters)

            # Serialize the filtered data
            serializer = MoneyReceiptSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class UpdateMoneyReceiptView(APIView):    
    def post(self, request, *args, **kwargs):
        data = request.data
        delivery_statement_id = data.get('id')  
        lr_booking_ids = data.pop('lr_booking', [])
        party_billing_ids = data.get('party_billing', [])
        pay_type = data.get('pay_type', None)

        if not delivery_statement_id:
            return Response({
                "message": "ID of the Money Receipt record is required.",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the PartyBilling instance
            try:
                money_receipt = MoneyReceipt.objects.get(id=delivery_statement_id, is_active=True, flag=True)
            except MoneyReceipt.DoesNotExist:
                return Response({
                    "message": f"Money Receipt with id {delivery_statement_id} does not exist or is inactive.",
                    "status": "error"
                }, status=status.HTTP_404_NOT_FOUND)

            # Store unique PartyMaster objects
            party_masters = set()    

            # Validate each LR_Bokking in the requested list
            for lr_no in lr_booking_ids:
                # Get the LR_Bokking object
                try:
                    lr_booking = LR_Bokking.objects.get(lr_no=lr_no)
                except LR_Bokking.DoesNotExist:
                    return Response({
                        "message": f"LR_Bokking with lr_no {lr_no} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 1: Ensure lr_booking is not already associated with another active VoucherReceiptBranch
                if MoneyReceipt.objects.filter(
                    lr_booking=lr_booking,
                    is_active=True,
                    flag=True
                ).exclude(id=delivery_statement_id).exists():
                    return Response({
                        "msg": f"LR_Bokking with lr_no {lr_no} is already associated with another active MoneyReceipt.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 2: Check pay_type               
                if int(lr_booking.pay_type_id) != 1 and int(lr_booking.pay_type_id) != 2:
                    return Response({
                        "msg": f"LR_Bokking with lr_no {lr_no} has not pay_type 'Paid' or 'TOPAY'.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Add billing_party to the set
                if lr_booking.billing_party:
                    party_masters.add(lr_booking.billing_party)
            
             # Validate each party_billing in the requested list
            for party_bill in party_billing_ids:
                # Get the LR_Bokking object
                try:
                    party_billing = PartyBilling.objects.get(id=party_bill)
                except PartyBilling.DoesNotExist:
                    return Response({
                        "message": f"party_billing with lr_no {party_bill} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)                
                
                # Validation 1: Ensure party_billing is not already associated with an active PartyBilling                
                if MoneyReceipt.objects.filter(
                    party_billing=party_billing,
                    is_active=True,
                    flag=True
                ).exclude(id=delivery_statement_id).exists():
                    return Response({
                        "msg": f"Party_billing with lr_no {party_bill} is already associated with an active Money Receipt.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Add billing_party to the set
                if party_billing.billing_party:
                    party_masters.add(party_billing.billing_party)

            # Ensure all billing_party objects are the same
            if len(party_masters) > 1:
                return Response({
                    "msg": "All lr_booking and party_billing entries must have the same billing_party.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)               

            # Validation for pay_type-specific fields and ensuring irrelevant fields are blank/null
            if pay_type == "UPI":
                if not data.get("utr_no"):
                    return Response({
                        "msg": "For 'UPI' pay_type, 'utr_no' is required.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Ensure unrelated fields are null/blank
                data["rtgs_no"] = None
                data["bank_name"] = None
                data["check_no"] = None
                data["check_date"] = None

            elif pay_type == "RTGS/NFT":
                if not data.get("rtgs_no"):
                    return Response({
                        "msg": "For 'RTGS/NFT' pay_type, 'rtgs_no' is required.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Ensure unrelated fields are null/blank
                data["utr_no"] = None
                data["bank_name"] = None
                data["check_no"] = None
                data["check_date"] = None

            elif pay_type == "CHECK":
                if not data.get("bank_name"):
                    return Response({
                        "msg": "For 'CHECK' pay_type, 'bank_name' is required.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                if not data.get("check_no"):
                    return Response({
                        "msg": "For 'CHECK' pay_type, 'check_no' is required.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                if not data.get("check_date"):
                    return Response({
                        "msg": "For 'CHECK' pay_type, 'check_date' is required.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Ensure unrelated fields are null/blank
                data["utr_no"] = None
                data["rtgs_no"] = None

            else:
                return Response({
                    "msg": "Invalid pay_type provided.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            # If all validations pass, proceed with the update
            with transaction.atomic():
                serializer = MoneyReceiptSerializer(money_receipt, data=data, partial=True)
                if serializer.is_valid():
                    updated_money_receipt = serializer.save(updated_by=request.user)

                    # Update LR_Bokking entries in the ManyToMany field
                    if lr_booking_ids:
                        lr_bookings = LR_Bokking.objects.filter(lr_no__in=lr_booking_ids)
                        if len(lr_bookings) != len(lr_booking_ids):
                            raise ValueError("One or more LR_Booking IDs not found.")
                        updated_money_receipt.lr_booking.set(lr_bookings)
                    else:
                        # Clear all related LR_Bokking if list is empty
                        updated_money_receipt.lr_booking.clear()

                    # Add LR_Bokking entries to the ManyToMany field
                    if party_billing_ids:
                        party_billings = PartyBilling.objects.filter(id__in=party_billing_ids)
                        if len(party_billings) != len(party_billing_ids):
                            raise ValueError("One or more party_billings IDs not found.")
                        updated_money_receipt.party_billing.set(party_billings)
                    else:
                        # Clear all related PartyBilling if list is empty
                        updated_money_receipt.party_billing.clear()

                    response_serializer = MoneyReceiptSerializer(updated_money_receipt)
                    return Response({
                        "message": "Voucher Receipt Branch updated successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_200_OK)

                return Response({
                    "message": "Failed to update Voucher Receipt Branch",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "message": "An error occurred while updating Voucher Receipt Branch",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class MoneyReceiptSoftDeleteAPIView(APIView):
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
            instance = MoneyReceipt.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'Money Receipt deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except MoneyReceipt.DoesNotExist:
            return Response({
                'msg': 'Money Receipt not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class MoneyReceiptPermanentDeleteAPIView(APIView):
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
            instance = MoneyReceipt.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'Money Receipt permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except MoneyReceipt.DoesNotExist:
            return Response({
                'msg': 'Money Receipt not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)


class VoucherPaymentTypeCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            serializer = VoucherPaymentTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response({
                    'status': 'success',
                    'message': 'Voucher Payment Type created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Validation failed.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An error occurred.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoucherPaymentTypeRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = VoucherPaymentType.objects.get(pk=gst_id)
            serializer = VoucherPaymentTypeSerializer(instance)
            return Response({'msg': 'Voucher Payment Type retrieved successfully', 'status': 'success', 'data': [serializer.data]}, status=status.HTTP_200_OK)
        except VoucherPaymentType.DoesNotExist:
            return Response({'msg': 'Voucher Payment Type not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

class VoucherPaymentTypeRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all GSTMaster instances where `flag=True`, ordered by `id` in descending order
            instances = VoucherPaymentType.objects.filter(flag=True).order_by('-id')
            serializer = VoucherPaymentTypeSerializer(instances, many=True)

            # Custom response structure
            response_data = {
                'msg': 'Voucher Payment Type records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving Voucher Payment Type records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoucherPaymentTypeRetrieveFilteredView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve active GSTMaster records where `is_active=True` and `flag=True`, ordered by `id` in descending order
            queryset = VoucherPaymentType.objects.filter(is_active=True, flag=True).order_by('-id')
            serializer = VoucherPaymentTypeSerializer(queryset, many=True)

            # Custom response structure
            response_data = {
                'msg': 'Filtered Voucher Payment Type records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving filtered Voucher Payment Type records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoucherPaymentTypeUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = VoucherPaymentType.objects.get(pk=gst_id)
            serializer = VoucherPaymentTypeSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({'msg': 'Voucher Payment Type updated successfully', 'status': 'success', 'data': [serializer.data]}, status=status.HTTP_200_OK)
            return Response({'msg': 'Validation failed', 'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except VoucherPaymentType.DoesNotExist:
            return Response({'msg': 'Voucher Payment Type not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

class VoucherPaymentTypeDeleteView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = VoucherPaymentType.objects.get(pk=gst_id)
            instance.flag = False
            instance.save()
            return Response({'msg': 'Voucher Payment Type soft deleted successfully', 'status': 'success', 'data': {}}, status=status.HTTP_200_OK)
        except VoucherPaymentType.DoesNotExist:
            return Response({'msg': 'Voucher Payment Type not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)



class GenerateVoucherPaymentBranchPDF(APIView):
    def get(self, request, delivery_no):
        # Fetch the statement details based on delivery_no
        statement = get_object_or_404(VoucherPaymentBranch, voucher_no=delivery_no)

        # Fetch company details
        company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

        # Generate barcode for the delivery_no
        barcode_base64 = generate_barcode(delivery_no)

        # Get the logged-in user's name
        user_profile = UserProfile.objects.get(user=statement.created_by)
        user_name = user_profile.first_name + " "+user_profile.last_name

        # Render HTML to string
        html_string = render(request, 'Vouch_pay_branch/Vouch_pay_branch.html', {
            'company': company,
            'statement': statement,       
            'barcode_base64': barcode_base64,
            'user_name': user_name,
        }).content.decode('utf-8')

        # Define CSS
        css = CSS(string=''' 
            @page {
                size: legal;
                margin: 5mm;
            }
        ''')

        # Generate PDF
        html = HTML(string=html_string)
        pdf = html.write_pdf(stylesheets=[css])

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=Vouch_pay_branch_{delivery_no}.pdf'

        # Handle branch manager print status
        if request.user.userprofile.role == 'branch_manager':
            if statement.printed_by_branch_manager:
                return Response({"msg": "This statement has already been printed by a branch manager.", 'status': 'error'}, status=400)
            statement.printed_by_branch_manager = True
            statement.save()

        return response

class GenerateVoucherPaymentBranchVoucherNumberrViews(APIView):   
    def post(self, request, *args, **kwargs):
        print(request.data)
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
            last_booking_memo = VoucherPaymentBranch.objects.filter(
                branch_name_id=branch_id,
                voucher_no__startswith=prefix
            ).exclude(voucher_no__isnull=True).exclude(voucher_no__exact='').order_by('-voucher_no').first()

            if last_booking_memo:
                last_sequence_number = int(last_booking_memo.voucher_no[len(prefix):])
                new_delivery_no = f"{prefix}{str(last_sequence_number + 1).zfill(5)}"
            else:
                new_delivery_no = f"{prefix}00001"

            # On successful LR number generation
            response_data = {
                'msg': 'voucher_no number generated successfully',
                'status': 'success',
                'data': {
                    'voucher_no': new_delivery_no
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
                'message': 'An error occurred during voucher_no generation due to invalid data.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any other unexpected exceptions
            response_data = {
                'status': 'error',
                'message': 'An error occurred while generating the voucher_no.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoucherPaymentBranchCreateView(APIView):    
    def post(self, request, *args, **kwargs):
        try:
            # Extract and validate required fields
            branch_name = request.data.get('branch_name')
            date = request.data.get('date')
            amount = request.data.get('amount')

            if not branch_name or not date or not amount:
                return Response({
                    'status': 'error',
                    'message': "Fields 'branch_name', 'date', and 'amount' are mandatory."
                }, status=status.HTTP_400_BAD_REQUEST)

            if Decimal(amount) == 0:
                return Response({
                    'status': 'error',
                    'message': "'amount' cannot be zero."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate the branch exists
            try:
                BranchMaster.objects.get(id=branch_name, is_active=True, flag=True)
            except BranchMaster.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': f"Branch with id {branch_name} does not exist or is inactive."
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = VoucherPaymentBranchSerializer(data=request.data)
            if serializer.is_valid():
                with transaction.atomic():
                    # Save the VoucherPaymentBranch object
                    voucher_payment_branch = serializer.save(created_by=request.user)

                    # Perform the debit operation using CashBook
                    cash_book = CashBook()
                    cash_book.debit_operation(
                        branch_id=branch_name,
                        date=date,
                        amount=Decimal(amount),
                        payment_id=voucher_payment_branch.id
                    )

                    # Return success response
                    return Response({
                        'status': 'success',
                        'message': 'Voucher Payment Branch created successfully.',
                        'data': [serializer.data]
                    }, status=status.HTTP_201_CREATED)

            return Response({
                'status': 'error',
                'message': 'Validation failed.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An error occurred.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoucherPaymentBranchRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = VoucherPaymentBranch.objects.get(pk=gst_id)
            serializer = VoucherPaymentBranchSerializer(instance)
            return Response({'msg': 'Voucher Payment Branch retrieved successfully', 'status': 'success', 'data': [serializer.data]}, status=status.HTTP_200_OK)
        except VoucherPaymentBranch.DoesNotExist:
            return Response({'msg': 'Voucher Payment Branch not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

class VoucherPaymentBranchRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            branch_id = request.data.get("branch_id")
            user_profile = UserProfile.objects.get(user=request.user)            
            allowed_branches = user_profile.branches.all()
            if not branch_id:
                return Response({
                    "status": "error",
                    "message": "Branch ID is required."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Retrieve all GSTMaster instances where `flag=True`, ordered by `id` in descending order
            instances = VoucherPaymentBranch.objects.filter(
                flag=True
                ).filter(
                Q(branch_name__in=allowed_branches)
                ).filter(
                Q(branch_name_id=branch_id)
                ).order_by('-id')
            serializer = VoucherPaymentBranchSerializer(instances, many=True)

            # Custom response structure
            response_data = {
                'msg': 'Voucher Payment Branch records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving Voucher Payment Branch records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoucherPaymentBranchFilterView(APIView): 
    def post(self, request, *args, **kwargs):
        try:
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(VoucherPaymentBranch, filters)

            # Serialize the filtered data
            serializer = VoucherPaymentBranchSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class VoucherPaymentBranchRetrieveFilteredView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve active GSTMaster records where `is_active=True` and `flag=True`, ordered by `id` in descending order
            queryset = VoucherPaymentBranch.objects.filter(is_active=True, flag=True).order_by('-id')
            serializer = VoucherPaymentBranchSerializer(queryset, many=True)

            # Custom response structure
            response_data = {
                'msg': 'Filtered Voucher Payment Branch records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving filtered Voucher Payment Branch records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VoucherPaymentBranchUpdateView(APIView):    
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        branch_name = request.data.get('branch_name')
        date = request.data.get('date')
        amount = request.data.get('amount')

        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        
        if not branch_name or not date or not amount:
            return Response({
                    'status': 'error',
                    'message': "Fields 'branch_name', 'date', and 'amount' are mandatory."
            }, status=status.HTTP_400_BAD_REQUEST)

        if Decimal(amount) == 0:
            return Response({
                    'status': 'error',
                    'message': "'amount' cannot be zero."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate the branch exists
        try:
            BranchMaster.objects.get(id=branch_name, is_active=True, flag=True)
        except BranchMaster.DoesNotExist:
            return Response({
                    'status': 'error',
                    'message': f"Branch with id {branch_name} does not exist or is inactive."
            }, status=status.HTTP_400_BAD_REQUEST)
                
        try:
            with transaction.atomic():
                instance = VoucherPaymentBranch.objects.get(pk=gst_id)
                if (Decimal(amount)!=instance.amount):
                    # Validate `CashBook` Record
                    cash_book = CashBook.objects.filter(branch_name_id=branch_name, date=date).first()
                    if not cash_book:
                        # Check for last record by branch
                        cash_book = CashBook.objects.filter(branch_name_id=branch_name, date__lt=date).order_by('-date').first()
                        if not cash_book:
                            raise ValueError(f"CashBook record not found for to update debit record.")
                    # Check for subsequent entries
                    subsequent_entries = CashBook.objects.filter(branch_name_id=branch_name, date__gt=cash_book.date).exists()
                    if subsequent_entries:
                        raise ValueError(f"You cannot update the amount because the next day cash book record is based on this VoucherPaymentBranch")
                    
                    difference = Decimal(amount) - instance.amount                  
                    cash_book.closing_balance += abs(difference)
                    cash_book.save()

                serializer = VoucherPaymentBranchSerializer(instance, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save(updated_by=request.user)
                    return Response({'msg': 'Voucher Payment Branch updated successfully', 'status': 'success', 'data': [serializer.data]}, status=status.HTTP_200_OK)
                return Response({'msg': 'Validation failed', 'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except VoucherPaymentBranch.DoesNotExist:
            return Response({'msg': 'Voucher Payment Branch not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "An error occurred while updating Voucher Payment Branch",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class VoucherPaymentBranchDeleteView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = VoucherPaymentBranch.objects.get(pk=gst_id)
            instance.flag = False
            instance.save()
            return Response({'msg': 'Voucher Payment Branch soft deleted successfully', 'status': 'success', 'data': {}}, status=status.HTTP_200_OK)
        except VoucherPaymentBranch.DoesNotExist:
            return Response({'msg': 'Voucher Payment Branch not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)



class CreditOperationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract parameters from the request
            branch_id = request.data.get('branch_id')
            voucher_id = request.data.get('voucher_id')
            date = request.data.get('date')
            amount = request.data.get('amount')

            # Validate input
            if not all([branch_id, voucher_id, date, amount]):
                return Response(
                    {"error": "All parameters (branch_id, voucher_id, date, amount) are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Perform credit operation
            cash_book = CashBook()
            cash_book = cash_book.credit_operation(branch_id, voucher_id, date, Decimal(amount))
            return Response(
                {
                    "message": "Credit operation completed successfully.",
                    "cash_book_id": cash_book.id,
                    "closing_balance": str(cash_book.closing_balance),
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DebitOperationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract parameters from the request
            branch_id = request.data.get('branch_id')
            payment_id = request.data.get('payment_id')
            date = request.data.get('date')
            amount = request.data.get('amount')

            # Validate input
            if not all([branch_id, payment_id, date, amount]):
                return Response(
                    {"error": "All parameters (branch_id, payment_id, date, amount) are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Perform debit operation
            cash_book = CashBook()
            cash_book = cash_book.debit_operation(branch_id, payment_id, date, Decimal(amount))
            return Response(
                {
                    "message": "Debit operation completed successfully.",
                    "cash_book_id": cash_book.id,
                    "closing_balance": str(cash_book.closing_balance),
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateCashBookPDF(APIView):
    def get(self, request, delivery_no):
        # Fetch the statement details based on delivery_no
        statement = get_object_or_404(CashBook, id=delivery_no)
        credits = statement.credit.all()
        debits = statement.debit.all()

        # Fetch company details
        company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

        # Generate barcode for the delivery_no
        barcode_base64 = generate_barcode(delivery_no)

        # Get the logged-in user's name
        user_name = request.user.get_full_name() or request.user.username

        # Render HTML to string
        html_string = render(request, 'cashbook/cashbook.html', {
            'company': company,
            'statement': statement,
            'credits': credits,
            'debits': debits,
            'barcode_base64': barcode_base64,
            'user_name': user_name,
        }).content.decode('utf-8')

        # Define CSS
        css = CSS(string=''' 
            @page {
                size: legal;
                margin: 5mm;
            }
        ''')

        # Generate PDF
        html = HTML(string=html_string)
        pdf = html.write_pdf(stylesheets=[css])

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=cashbook_{delivery_no}.pdf'

        # Handle branch manager print status
        if request.user.userprofile.role == 'branch_manager':
            if statement.printed_by_branch_manager:
                return Response({"msg": "This statement has already been printed by a branch manager.", 'status': 'error'}, status=400)
            statement.printed_by_branch_manager = True
            statement.save()

        return response

class CashBookRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        try:
            # Extract branch_id and date from request
            branch_id = request.data.get('branch_id')
            date = request.data.get('date')

            # Validate required fields
            if not branch_id or not date:
                return Response({
                    'status': 'error',
                    'message': "Fields 'branch_id' and 'date' are mandatory."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Filter CashBook by branch and date
            cash_book = CashBook.objects.filter(branch_name_id=branch_id, date=date).first()

            if not cash_book:
                cash_book = CashBook.objects.filter(branch_name_id=branch_id, date__gt=date).order_by('date').first()
                if not cash_book:
                    # If no record found, retrieve the last record for the branch
                    cash_book = CashBook.objects.filter(branch_name_id=branch_id, date__lt=date).order_by('-date').first()

                    if not cash_book:
                        return Response({
                            'status': 'error',
                            'message': f"No records found for branch ID {branch_id} on or before {date}."
                        }, status=status.HTTP_404_NOT_FOUND)
                    return Response({
                        'status': 'success',
                        'message': 'CashBook record retrieved successfully.',
                        'data': {
                            "opening_balance": cash_book.closing_balance
                        }
                    }, status=status.HTTP_200_OK)

                # If no record found, retrieve the last record for the branch
                cash_book1 = CashBook.objects.filter(branch_name_id=branch_id, date__lt=date).order_by('-date').first()

                if not cash_book1:
                    return Response({
                        'status': 'error',
                        'message': f"No records found for branch ID {branch_id} on or before {date}."
                    }, status=status.HTTP_404_NOT_FOUND)
                return Response({
                    'status': 'success',
                    'message': 'CashBook record retrieved successfully.',
                    'data': {
                        "opening_balance": cash_book1.closing_balance,
                        "closing_balance": cash_book.opening_balance
                    }
                }, status=status.HTTP_200_OK)

            # Serialize CashBook object
            serializer = CashBookSerializer(cash_book)

            return Response({
                'status': 'success',
                'message': 'CashBook record retrieved successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred.',
                'error': str(e)  # Include error for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateBillingSubmissionPDF(APIView):
    def get(self, request, delivery_no):
        # Fetch the statement details based on delivery_no
        statement = get_object_or_404(BillingSubmission, sub_no=delivery_no)        

        # Fetch company details
        company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

        # Generate barcode for the delivery_no
        barcode_base64 = generate_barcode(delivery_no)

        # Get the logged-in user's name
        user_profile = UserProfile.objects.get(user=statement.created_by)
        user_name = user_profile.first_name + " "+user_profile.last_name

        # Render HTML to string
        html_string = render(request, 'billing_submission/billing_submission.html', {
            'company': company,
            'statement': statement,             
            'barcode_base64': barcode_base64,
            'user_name': user_name,
        }).content.decode('utf-8')

        # Define CSS
        css = CSS(string=''' 
            @page {
                size: legal;
                margin: 5mm;
            }
        ''')

        # Generate PDF
        html = HTML(string=html_string)
        pdf = html.write_pdf(stylesheets=[css])

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=Vouch_pay_branch_{delivery_no}.pdf'

        # Handle branch manager print status
        if request.user.userprofile.role == 'branch_manager':
            if statement.printed_by_branch_manager:
                return Response({"msg": "This statement has already been printed by a branch manager.", 'status': 'error'}, status=400)
            statement.printed_by_branch_manager = True
            statement.save()

        return response

class GenerateBillingSubmissionSubmissionNumberrViews(APIView):   
    def post(self, request, *args, **kwargs):
        print(request.data)
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
            last_booking_memo = BillingSubmission.objects.filter(
                branch_name_id=branch_id,
                sub_no__startswith=prefix
            ).exclude(sub_no__isnull=True).exclude(sub_no__exact='').order_by('-sub_no').first()

            if last_booking_memo:
                last_sequence_number = int(last_booking_memo.sub_no[len(prefix):])
                new_delivery_no = f"{prefix}{str(last_sequence_number + 1).zfill(5)}"
            else:
                new_delivery_no = f"{prefix}00001"

            # On successful LR number generation
            response_data = {
                'msg': 'Billing Submission number generated successfully',
                'status': 'success',
                'data': {
                    'sub_no': new_delivery_no
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
                'message': 'An error occurred during Billing Submission Number generation due to invalid data.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any other unexpected exceptions
            response_data = {
                'status': 'error',
                'message': 'An error occurred while generating the Billing Submission No.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BillingSubmissionCreateView(APIView):    
    def post(self, request, *args, **kwargs):
        print(request.data)
        try:
            # Extract the bill_no from the request data
            bill_no_id = request.data.get('bill_no')

            # Check if a record with the same bill_no, is_active=True, and flag=True exists
            if BillingSubmission.objects.filter(
                bill_no_id=bill_no_id, is_active=True, flag=True
            ).exists():
                # Fetch the existing record to include sub_no in the error message
                existing_submission = BillingSubmission.objects.filter(
                    bill_no_id=bill_no_id, is_active=True, flag=True
                ).first()
                return Response({
                    'status': 'error',
                    'message': f"For {existing_submission.sub_no}, there is already one active bill submitted with the requst bill_no."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Proceed with creation if no conflict is found
            serializer = BillingSubmissionSerializer(data=request.data)
            if serializer.is_valid():
                billing_submission = serializer.save(created_by=request.user)

                try:
                    # Try to generate PDF and send email
                    pdf_sent = True
                    recipient_list = []
                    email_addresses = [
                        billing_submission.bill_no.billing_party.email_id.strip()
                    ]            
                    for email in email_addresses:
                        try:
                            validate_email(email)  
                            recipient_list.append(email)  
                        except ValidationError:                    
                            continue

                    # Generate PDF
                    lr_no = billing_submission.sub_no
                    pdf_response = GenerateBillingSubmissionPDF().get(request, lr_no)
                    pdf_path = f"/tmp/invoice_{lr_no}.pdf"
                    with open(pdf_path, 'wb') as pdf_file:
                        pdf_file.write(pdf_response.content)

                    # Send email with PDF attachment
                    subject = "Bill Submission Done."
                    message = "Your Bill Submission done successfully. Please find the attached invoice."
                    if recipient_list:
                        send_email_with_attachment(subject, message, recipient_list, pdf_path)

                    # Remove temporary PDF file
                    os.remove(pdf_path)
                except Exception as email_error:
                    pdf_sent = False
                    # Log or handle the error if needed
                    print(f"Failed to send email or generate PDF: {str(email_error)}")

                if pdf_sent:
                    return Response({
                        'status': 'success',
                        'message': 'Billing Submission created successfully.',
                        'data': [serializer.data]
                    }, status=status.HTTP_201_CREATED)
                else :
                    return Response({
                        'status': 'success',
                        'message': 'Billing Submission created successfully, but failed to send email.',
                        'data': [serializer.data]
                    }, status=status.HTTP_201_CREATED)

            # Return validation errors
            return Response({
                'status': 'error',
                'message': 'Validation failed.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BillingSubmissionRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = BillingSubmission.objects.get(pk=gst_id)
            serializer = BillingSubmissionSerializer(instance)
            return Response({'msg': 'Billing Submission retrieved successfully', 'status': 'success', 'data': [serializer.data]}, status=status.HTTP_200_OK)
        except BillingSubmission.DoesNotExist:
            return Response({'msg': 'Billing Submission not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

class BillingSubmissionRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            branch_id = request.data.get("branch_id")
            user_profile = UserProfile.objects.get(user=request.user)            
            allowed_branches = user_profile.branches.all()

            if not branch_id:
                return Response({
                    "status": "error",
                    "message": "Branch ID is required."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve all GSTMaster instances where `flag=True`, ordered by `id` in descending order
            instances = BillingSubmission.objects.filter(
                flag=True
                ).filter(
                Q(branch_name__in=allowed_branches) 
                ).filter(
                Q(branch_name_id=branch_id)
                ).order_by('-id')
            serializer = BillingSubmissionSerializer(instances, many=True)

            # Custom response structure
            response_data = {
                'msg': 'Billing Submission records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving Billing Submission records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BillingSubmissionRetrieveFilteredView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve active GSTMaster records where `is_active=True` and `flag=True`, ordered by `id` in descending order
            queryset = BillingSubmission.objects.filter(is_active=True, flag=True).order_by('-id')
            serializer = BillingSubmissionSerializer(queryset, many=True)

            # Custom response structure
            response_data = {
                'msg': 'Filtered Billing Submission records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving filtered Billing Submission records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BillingSubmissionFilterView(APIView): 
    def post(self, request, *args, **kwargs):
        try:
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(BillingSubmission, filters)

            # Serialize the filtered data
            serializer = BillingSubmissionSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class BillingSubmissionUpdateView(APIView):    
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response(
                {'msg': 'ID is required', 'status': 'error', 'data': {}},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            instance = BillingSubmission.objects.get(pk=gst_id)

            # Extract bill_no from the request data
            bill_no_id = request.data.get('bill_no')
            
            # Check for existing active BillingSubmission records with the same bill_no
            # Ensure the check excludes the current instance being updated
            if bill_no_id and BillingSubmission.objects.filter(
                bill_no_id=bill_no_id, is_active=True, flag=True
            ).exclude(pk=instance.pk).exists():
                existing_submission = BillingSubmission.objects.filter(
                    bill_no_id=bill_no_id, is_active=True, flag=True
                ).exclude(pk=instance.pk).first()
                return Response({
                    'msg': f"For {existing_submission.sub_no}, there is already one active bill submitted.",
                    'status': 'error',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Proceed with updating the instance
            serializer = BillingSubmissionSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'Billing Submission updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            # Return validation errors
            return Response({
                'msg': 'Validation failed',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except BillingSubmission.DoesNotExist:
            # Handle case where the instance does not exist
            return Response({
                'msg': 'Billing Submission not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class BillingSubmissionDeleteView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = BillingSubmission.objects.get(pk=gst_id)
            instance.flag = False
            instance.save()
            return Response({'msg': 'Billing Submission soft deleted successfully', 'status': 'success', 'data': {}}, status=status.HTTP_200_OK)
        except GSTMaster.DoesNotExist:
            return Response({'msg': 'Billing Submission not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)




class DeductionReasonTypeCreateView(APIView):    
    def post(self, request, *args, **kwargs):
        try:
            serializer = DeductionReasonTypeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response({
                    'status': 'success',
                    'message': 'Deduction Reason Type created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            return Response({
                'status': 'error',
                'message': 'Validation failed.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An error occurred.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeductionReasonTypeRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = DeductionReasonType.objects.get(pk=gst_id)
            serializer = DeductionReasonTypeSerializer(instance)
            return Response({'msg': 'Deduction Reason Type retrieved successfully', 'status': 'success', 'data': [serializer.data]}, status=status.HTTP_200_OK)
        except DeductionReasonType.DoesNotExist:
            return Response({'msg': 'Deduction Reason Type not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

class DeductionReasonTypeRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all GSTMaster instances where `flag=True`, ordered by `id` in descending order
            instances = DeductionReasonType.objects.filter(flag=True).order_by('-id')
            serializer = DeductionReasonTypeSerializer(instances, many=True)

            # Custom response structure
            response_data = {
                'msg': 'Deduction Reason Type records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving Deduction Reason Type records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeductionReasonTypeRetrieveFilteredView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve active GSTMaster records where `is_active=True` and `flag=True`, ordered by `id` in descending order
            queryset = DeductionReasonType.objects.filter(is_active=True, flag=True).order_by('-id')
            serializer = DeductionReasonTypeSerializer(queryset, many=True)

            # Custom response structure
            response_data = {
                'msg': 'Filtered Deduction Reason Type records retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected errors
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving filtered Deduction Reason Type records.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeductionReasonTypeUpdateView(APIView):
    def post(self, request, *args, **kwargs):        
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = DeductionReasonType.objects.get(pk=gst_id)
            serializer = DeductionReasonTypeSerializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({'msg': 'Deduction Reason Type updated successfully', 'status': 'success', 'data': [serializer.data]}, status=status.HTTP_200_OK)
            return Response({'msg': 'Validation failed', 'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except DeductionReasonType.DoesNotExist:
            return Response({'msg': 'Deduction Reason Type not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)

class DeductionReasonTypeDeleteView(APIView):
    def post(self, request, *args, **kwargs):
        gst_id = request.data.get('id')
        if not gst_id:
            return Response({'msg': 'ID is required', 'status': 'error', 'data': {}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance = DeductionReasonType.objects.get(pk=gst_id)
            instance.flag = False
            instance.save()
            return Response({'msg': 'Deduction Reason Type soft deleted successfully', 'status': 'success', 'data': {}}, status=status.HTTP_200_OK)
        except DeductionReasonType.DoesNotExist:
            return Response({'msg': 'Deductio Reason Type not found', 'status': 'error', 'data': {}}, status=status.HTTP_404_NOT_FOUND)


class DeductionView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract fields from the request data
        lr_booking_id = request.data.get("lr_booking")
        party_billing_id = request.data.get("party_billing")
        deduct_amt = Decimal(str(request.data.get("deduct_amt", "0.00")))
        reason_id = request.data.get("reason")
        remarks = request.data.get("remarks", "")
        created_by_id = request.user
        
        
        # Validate the request input
        if not lr_booking_id and not party_billing_id:
            return Response(
                {"msg": "Either 'lr_booking' or 'party_billing' must be provided.", "status": "error", "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure only one of lr_booking or party_billing is provided
        if lr_booking_id and party_billing_id:
            return Response(
                {"msg": "Only one of 'lr_booking' or 'party_billing' can be provided.", "status": "error", "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if lr_booking_id:
                # Check if lr_booking is valid
                if str(lr_booking_id).strip() in ["0", "None", "undefined"]:
                    return Response(
                        {"msg": "'lr_booking' is invalid.", "status": "error", "data": None},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check for existing record
                lr_booking = LR_Bokking.objects.get(lr_no=lr_booking_id)
                deduction = Deduction.objects.filter(lr_booking_id=lr_booking_id).first()
                if deduction:
                    prev_deduct_amt = deduction.deduct_amt or Decimal(0.00)
                    diff = deduct_amt - prev_deduct_amt
                    if diff > 0:
                        lr_booking.grand_total -= diff
                    else:
                        lr_booking.grand_total += abs(diff)

                    # Update existing record
                    deduction.deduct_amt = deduct_amt
                    deduction.reason_id = reason_id
                    deduction.remarks = remarks
                    deduction.updated_by = created_by_id
                    deduction.save()
                    lr_booking.save()
                    msg = "Deduction updated successfully."
                else:
                    lr_booking.grand_total = lr_booking.grand_total - deduct_amt
                    # Create a new record
                    deduction = Deduction.objects.create(
                        lr_booking_id=lr_booking_id,
                        deduct_amt=deduct_amt,
                        reason_id=reason_id,
                        remarks=remarks,
                        created_by=created_by_id,
                    )
                    lr_booking.save()
                    msg = "Deduction created successfully."

            elif party_billing_id:
                # Check if party_billing is valid
                if str(party_billing_id).strip() in ["0", "None", "undefined"]:
                    return Response(
                        {"msg": "'party_billing' is invalid.", "status": "error", "data": None},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check for existing record
                party_billing = PartyBilling.objects.get(id=party_billing_id)
                deduction = Deduction.objects.filter(party_billing_id=party_billing_id).first()
                if deduction:
                    prev_deduct_amt = deduction.deduct_amt or Decimal(0.00)
                    diff = deduct_amt - prev_deduct_amt
                    if diff > 0:
                        party_billing.total_amt -= diff
                    else:
                        party_billing.total_amt += abs(diff)
                    # Update existing record
                    deduction.deduct_amt = deduct_amt
                    deduction.reason_id = reason_id
                    deduction.remarks = remarks
                    deduction.updated_by = created_by_id
                    deduction.save()
                    party_billing.save()
                    msg = "Deduction updated successfully."
                else:
                    party_billing.total_amt -= deduct_amt
                    # Create a new record
                    deduction = Deduction.objects.create(
                        party_billing_id=party_billing_id,
                        deduct_amt=deduct_amt,
                        reason_id=reason_id,
                        remarks=remarks,
                        created_by=created_by_id,
                    )
                    party_billing.save()
                    msg = "Deduction created successfully."

            # Serialize the deduction object
            serializer = DeductionSerializer(deduction)
            return Response({"msg": msg, "status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"msg": "An error occurred.", "status": "error", "data": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DeductionRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract fields from the request data
        lr_booking_id = request.data.get("lr_booking")
        party_billing_id = request.data.get("party_billing")
        
        # Validate the request input
        if not lr_booking_id and not party_billing_id:
            return Response(
                {"msg": "Either 'lr_booking' or 'party_billing' must be provided.", "status": "error", "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure only one of lr_booking or party_billing is provided
        if lr_booking_id and party_billing_id:
            return Response(
                {"msg": "Only one of 'lr_booking' or 'party_billing' can be provided.", "status": "error", "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if lr_booking_id:
                # Validate the lr_booking input
                if str(lr_booking_id).strip() in ["0", "None", "undefined"]:
                    return Response(
                        {"msg": "'lr_booking' is invalid.", "status": "error", "data": None},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Retrieve record based on lr_booking
                deduction = Deduction.objects.filter(lr_booking_id=lr_booking_id).first()
                if not deduction:
                    return Response(
                        {"msg": "No record found for the provided 'lr_booking'.", "status": "error", "data": None},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            elif party_billing_id:
                # Validate the party_billing input
                if str(party_billing_id).strip() in ["0", "None", "undefined"]:
                    return Response(
                        {"msg": "'party_billing' is invalid.", "status": "error", "data": None},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Retrieve record based on party_billing
                deduction = Deduction.objects.filter(party_billing_id=party_billing_id).first()
                if not deduction:
                    return Response(
                        {"msg": "No record found for the provided 'party_billing'.", "status": "error", "data": None},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Serialize the deduction object
            serializer = DeductionSerializer(deduction)
            return Response({"msg": "Deduction retrieved successfully.", "status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"msg": "An error occurred.", "status": "error", "data": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
