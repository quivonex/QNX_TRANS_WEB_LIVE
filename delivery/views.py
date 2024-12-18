from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from .models import LR_Bokking,TruckUnloadingReportStatus,TruckUnloadingReportDetails,TruckUnloadingReport,LocalMemoDelivery,DeliveryStatement,CustomerOutstanding,CustomerOutstanding
from branches.models import BranchMaster
from .serializers import TruckUnloadingReportStatusSerializer,TruckUnloadingReportDetailsSerializer,TruckUnloadingReportSerializer,LocalMemoDeliverySerializer,DeliveryStatementSerializer,CustomerOutstandingSerializer
from collection.models import BookingMemo, TripMemo
from rest_framework.exceptions import ValidationError
from decimal import Decimal
from weasyprint import HTML, CSS
from django.http import HttpResponse
from company.models import CompanyMaster
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64
from users.models import UserProfile
from rest_framework.exceptions import ValidationError
from company.filters import apply_filters
from account.models import VoucherReceiptBranch,MoneyReceipt
from django.db.models import Q
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from company.views import send_email_with_attachment
import os
from django.utils import timezone


class TURStatusCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            
            # Initialize the serializer with the request data
            serializer = TruckUnloadingReportStatusSerializer(data=request.data)
            
            # Validate the serializer
            if serializer.is_valid():
                # Save the instance with the user from the request
                serializer.save(created_by=request.user)
                
                # Return a success response with the serialized data
                return Response({
                    'message': 'Truck Unloading Report Status created successfully!',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'message': 'Error creating Truck Unloading Report Status',
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

class TURStatusRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        TUR_id = request.data.get('id')

        # Check if 'id' is provided
        if not TUR_id:
            return Response({
                'message': 'Truck Unloading Report Status ID is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the StandardRate instance
            tur = TruckUnloadingReportStatus.objects.get(id=TUR_id)
        except TruckUnloadingReportStatus.DoesNotExist:
            return Response({
                'message': 'Truck Unloading Report Status not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = TruckUnloadingReportStatusSerializer(tur)

        # Return the data with success status
        return Response({
            'message': 'Truck Unloading Report Status retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    
class TURStatusRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = TruckUnloadingReportStatus.objects.filter(flag=True).order_by('-id')

            # Serialize the items data
            serializer = TruckUnloadingReportStatusSerializer(items, many=True)

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
    
class TURStatusRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter the queryset for active StandardRate instances
            queryset = TruckUnloadingReportStatus.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = TruckUnloadingReportStatusSerializer(queryset, many=True)

            # Prepare the response data
            response_data = {
                'msg': 'Truck Unloading Report Status retrieved successfully',
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
    
class TURStatusUpdateAPIView(APIView):
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
            instance = TruckUnloadingReportStatus.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = TruckUnloadingReportStatusSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'Truck Unloading Report Status updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update Truck Unloading Report Status',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except TruckUnloadingReportStatus.DoesNotExist:
            return Response({
                'msg': 'Truck Unloading Report Status not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TURStatusSoftDeleteAPIView(APIView):
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
            instance = TruckUnloadingReportStatus.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'Truck Unloading Report Status deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except TruckUnloadingReportStatus.DoesNotExist:
            return Response({
                'msg': 'Truck Unloading Report Status not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class TURStatusPermanentDeleteAPIView(APIView):
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
            instance = TruckUnloadingReportStatus.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'Truck Unloading Report Status permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except TruckUnloadingReportStatus.DoesNotExist:
            return Response({
                'msg': 'Truck Unloading Report Status not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)



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

class GenerateTruckUnloadingReportPDF(APIView):
    def get(self, request, tur_no):
        # Fetch the report details based on tur_no
        report = get_object_or_404(TruckUnloadingReport, tur_no=tur_no)
        details = report.tur_details.all()

        # Fetch company details
        company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

        # Generate barcode for the tur_no
        barcode_base64 = generate_barcode(tur_no)

        # Get the logged-in user's name
        user_profile = UserProfile.objects.get(user=report.created_by)
        user_name = user_profile.first_name + " "+user_profile.last_name

        # Render HTML to string
        html_string = render(request, 'reports/truck_unloading_report_pdf.html', {
            'company': company,
            'report': report,
            'details': details,
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
        response['Content-Disposition'] = f'inline; filename=tur_{tur_no}.pdf'

        # Handle branch manager print status
        if request.user.userprofile.role == 'branch_manager':
            if report.printed_by_branch_manager:
                return Response({"msg": "This report has already been printed by a branch manager.", 'status': 'error'}, status=400)
            report.printed_by_branch_manager = True
            report.save()

        return response

class GenerateTURNumberView(APIView):
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
            last_booking_memo = TruckUnloadingReport.objects.filter(
                branch_name_id=branch_id,
                tur_no__startswith=prefix
            ).exclude(tur_no__isnull=True).exclude(tur_no__exact='').order_by('-tur_no').first()

            if last_booking_memo:
                last_sequence_number = int(last_booking_memo.tur_no[len(prefix):])
                new_tur_no = f"{prefix}{str(last_sequence_number + 1).zfill(5)}"
            else:
                new_tur_no = f"{prefix}00001"

            # On successful LR number generation
            response_data = {
                'msg': 'TUR number generated successfully',
                'status': 'success',
                'data': {
                    'memo_no': new_tur_no
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
                'message': 'An error occurred during TUR number generation due to invalid data.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any other unexpected exceptions
            response_data = {
                'status': 'error',
                'message': 'An error occurred while generating the TUR number.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TURCreateView(APIView):    
    def post(self, request, *args, **kwargs):
        print(request.data)
        data = request.data
        tur_details = data.pop('tur_details_lrs', [])
        try:
            # Validate branch_name and memo_no's to_branch
            memo_no_id = data.get('memo_no')
            branch_name_id = data.get('branch_name')

            memo = BookingMemo.objects.filter(id=memo_no_id, is_active=True, flag=True).first()
            if not memo:
                return Response({
                    'msg': "Memo not found or is inactive.",
                    'status': 'error',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if memo.to_branch_id != branch_name_id:
                return Response({
                    'msg': "Memo's to_branch and TUR's login branch are not the same.",
                    'status': 'error',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            trip_memo = TripMemo.objects.filter(
                booking_memos__booking_memo=memo, 
                is_active=True, 
                flag=True
            ).first()

            if not trip_memo:
                return Response({
                    'msg': "This BookingMemo's TripMemo not Completed.",
                    'status': 'error',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if memo_no is already used in active TruckUnloadingReport
            active_tur = TruckUnloadingReport.objects.filter(
                memo_no_id=memo_no_id, is_active=True, flag=True
            ).exists()
            if active_tur:
                return Response({
                    'msg': "This memo_no is already associated with an active TruckUnloadingReport.",
                    'status': 'error',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Begin transaction
            with transaction.atomic():
                # Create the TruckUnloadingReport
                tur = TruckUnloadingReport.objects.create(
                    branch_name_id=branch_name_id,
                    tur_no=data['tur_no'],
                    date=data['date'],
                    memo_no_id=memo_no_id,
                    tur_remark=data.get('tur_remark', ''),
                    total_qty=data.get('total_qty',0),
                    total_weight=data.get('total_weight',0),
                    created_by=request.user
                )

                # Process and save tur_details
                not_ok_found = False
                email_recipients = set()  # To store unique email recipients           
                # Process and save tur_details
                for detail in tur_details:
                    lr_booking_id = detail.get('lr_booking')
                    lr_booking = LR_Bokking.objects.get(lr_no=lr_booking_id)
                    # Check if lr_booking is already in active TUR details
                    active_tur_detail = TruckUnloadingReportDetails.objects.filter(
                        lr_booking_id=lr_booking_id,
                        truckunloadingreport__branch_name=lr_booking.to_branch,
                        truckunloadingreport__is_active=True,
                        truckunloadingreport__flag=True
                    ).exists()

                    if active_tur_detail:
                        # return Response({
                        #     'msg': f"{lr_booking_id} this lr_booking TruckUnloadingReport already present as lr_booking.to_branch == TruckUnloadingReport_branch_name .",
                        #     'status': 'error',
                        #     'data': {}
                        # }, status=status.HTTP_400_BAD_REQUEST)
                        raise Exception(f"{lr_booking_id} this lr_booking TruckUnloadingReport already present as lr_booking.to_branch == TruckUnloadingReport_branch_name .")

                    # Save each detail
                    tur_detail = TruckUnloadingReportDetails.objects.create(
                        lr_booking_id=lr_booking_id,
                        status_id=detail.get('status'),
                        remark=detail.get('remark', ''),
                        okpackage=detail.get('okpackage', 0),
                        ngpackage=detail.get('ngpackage',0),
                        created_by=request.user
                    )

                    # Update lr_booking's okpackage if okpackage > 0
                    if tur_detail.okpackage > 0:
                        lr_booking.okpackage = tur_detail.okpackage
                        lr_booking.save()

                    # Check if status is not "OK"                  
                    if tur_detail.status_id != 1:
                        not_ok_found = True
                        # Add branch emails to the recipient list
                        if lr_booking.from_branch.email_id:                       
                            email_recipients.add(lr_booking.from_branch.email_id.strip())
                        if lr_booking.to_branch.email_id:                        
                            email_recipients.add(lr_booking.to_branch.email_id.strip())

                    tur.tur_details.add(tur_detail)
                    
                # After saving the TUR and details, update the availability of the vehicle and driver and Trip status
                if trip_memo.to_branch_id == branch_name_id:
                    # Update TripMemo and related fields
                    trip_memo.trip_mode = 'CLOSE'
                    trip_memo.save()

                    if trip_memo.vehicle_no:
                        trip_memo.vehicle_no.is_available = True
                        trip_memo.vehicle_no.save()

                    # if trip_memo.driver_name:
                    #     trip_memo.driver_name.is_available = True
                    #     trip_memo.driver_name.save()

                # Serialize and return the created TUR

                # If any status is not "OK", send an email
                if not_ok_found:                 
                    try:
                        pdf_response = GenerateTruckUnloadingReportPDF().get(request, tur.tur_no)
                        pdf_path = f"/tmp/invoice_{tur.id}.pdf"
                        with open(pdf_path, 'wb') as pdf_file:
                            pdf_file.write(pdf_response.content)                        
                        recipient_list = list(email_recipients)  # Convert set to list                       
                        subject = "Truck Unloading Report - Issues Found"
                        message = "Issues were found in the Truck Unloading Report. There is some items are not ok at delivery time."                  
                        send_email_with_attachment(subject, message, recipient_list, pdf_path)                        
                        # Remove temporary PDF file
                        os.remove(pdf_path)
                    except Exception as email_error:
                        print(f"Failed to send email or generate PDF: {str(email_error)}")

                serializer = TruckUnloadingReportSerializer(tur)
                return Response({
                    'msg': "TruckUnloadingReport created successfully.",
                    'status': 'success',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'msg': f"An error occurred: {str(e)}",
                'status': 'error',
                'data': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

class TURRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        TUR_id = request.data.get('id')

        # Check if 'id' is provided
        if not TUR_id:
            return Response({
                'message': 'Truck Unloading Report ID is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the StandardRate instance
            tur = TruckUnloadingReport.objects.get(id=TUR_id)
        except TruckUnloadingReport.DoesNotExist:
            return Response({
                'message': 'Truck Unloading Report not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = TruckUnloadingReportSerializer(tur)

        # Return the data with success status
        return Response({
            'message': 'Truck Unloading Report retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    
class TURRetrieveAllView(APIView):
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
            items = TruckUnloadingReport.objects.filter(
                flag=True
                ).filter(
                Q(branch_name__in=allowed_branches)
                ).filter(
                Q(branch_name_id=branch_id)
                ).order_by('-id')

            # Serialize the items data
            serializer = TruckUnloadingReportSerializer(items, many=True)

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
    
class TURRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter the queryset for active StandardRate instances
            queryset = TruckUnloadingReport.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = TruckUnloadingReportSerializer(queryset, many=True)

            # Prepare the response data
            response_data = {
                'msg': 'Truck Unloading Report retrieved successfully',
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

class TURFilterView(APIView): 
    def post(self, request, *args, **kwargs):
        try:
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(TruckUnloadingReport, filters)

            # Serialize the filtered data
            serializer = TruckUnloadingReportSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class TURUpdateAPIView(APIView):    
    def post(self, request, *args, **kwargs):
        print(request.data)
        data = request.data
        tur_details = data.pop('tur_details_lrs', [])       
        try:
            TUR_id = data.get('id')
            if not TUR_id:
                return Response({
                    'msg': "ID is required.",
                    'status': 'error',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)
            # Fetch the existing TruckUnloadingReport instance
            tur = TruckUnloadingReport.objects.filter(id=TUR_id).first()
            if not tur:
                return Response({
                    'msg': "TruckUnloadingReport not found ",
                    'status': 'error',
                    'data': {}
                }, status=status.HTTP_404_NOT_FOUND)

            # Validate branch_name and memo_no's to_branch
            memo_no_id = data.get('memo_no', tur.memo_no_id)
            branch_name_id = data.get('branch_name', tur.branch_name_id)

            memo = BookingMemo.objects.filter(id=memo_no_id, is_active=True, flag=True).first()
            if not memo:
                return Response({
                    'msg': "Memo not found or is inactive.",
                    'status': 'error',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)

            if memo.to_branch_id != branch_name_id:
                return Response({
                    'msg': "Memo's to_branch and TUR's login branch are not the same.",
                    'status': 'error',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            trip_memo = TripMemo.objects.filter(
                booking_memos__booking_memo=memo, 
                is_active=True, 
                flag=True
            ).first()

            if not trip_memo:
                return Response({
                    'msg': "This BookingMemo's TripMemo not Completed.",
                    'status': 'error',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if memo_no is already used in another active TruckUnloadingReport
            active_tur = TruckUnloadingReport.objects.filter(
                memo_no_id=memo_no_id, is_active=True, flag=True
            ).exclude(id=TUR_id).exists()
            if active_tur:
                return Response({
                    'msg': "This memo_no is already associated with another active TruckUnloadingReport.",
                    'status': 'error',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Begin transaction
            with transaction.atomic():
                # Update the TruckUnloadingReport fields
                tur.branch_name_id = branch_name_id
                tur.tur_no = data.get('tur_no', tur.tur_no)
                tur.date = data.get('date', tur.date)
                tur.memo_no_id = memo_no_id
                tur.tur_remark = data.get('tur_remark', tur.tur_remark)
                tur.total_qty = Decimal(data.get('total_qty', 0))
                tur.total_weight = Decimal(data.get('total_weight', 0))
                tur.updated_by = request.user
                tur.save()

                # Process and update tur_details
                if tur_details:
                    # Delete existing TruckUnloadingReportDetails related to this TUR
                    TruckUnloadingReportDetails.objects.filter(truckunloadingreport=tur).delete()
                    # Clear existing tur_details
                    tur.tur_details.clear()

                    for detail in tur_details:
                        lr_booking_id = detail.get('lr_booking')
                        lr_booking = LR_Bokking.objects.get(lr_no=lr_booking_id)
                        # Check if lr_booking is already in another active TUR detail
                        active_tur_detail = TruckUnloadingReportDetails.objects.filter(
                            lr_booking_id=lr_booking_id,
                            truckunloadingreport__branch_name=lr_booking.to_branch,
                            truckunloadingreport__is_active=True,
                            truckunloadingreport__flag=True
                        ).exclude(id=TUR_id).exists()

                        if active_tur_detail:
                            # return Response({
                            #     'msg': f"{lr_booking_id} this lr_booking TruckUnloadingReport already present as lr_booking.to_branch == TruckUnloadingReport_branch_name .",
                            #     'status': 'error',
                            #     'data': {}
                            # }, status=status.HTTP_400_BAD_REQUEST)
                            raise Exception(f"{lr_booking_id} this lr_booking TruckUnloadingReport already present as lr_booking.to_branch == TruckUnloadingReport_branch_name .")

                        # Save each updated detail
                        tur_detail = TruckUnloadingReportDetails.objects.create(
                            lr_booking_id=lr_booking_id,
                            status_id=detail.get('status'),
                            remark=detail.get('remark', ''),
                            okpackage=detail.get('okpackage', 0),
                            ngpackage=detail.get('ngpackage',0),
                            created_by=request.user
                        )

                        # Update lr_booking's okpackage if okpackage > 0
                        if tur_detail.okpackage > 0:
                            lr_booking.okpackage = tur_detail.okpackage
                            lr_booking.save()
                            
                        tur.tur_details.add(tur_detail)

                    # After saving the TUR and details, update the availability of the vehicle and driver and Trip status
                    if trip_memo.to_branch_id == branch_name_id:
                        # Update TripMemo and related fields
                        trip_memo.trip_mode = 'CLOSE'
                        trip_memo.save()

                        if trip_memo.vehicle_no:
                            trip_memo.vehicle_no.is_available = True
                            trip_memo.vehicle_no.save()

                        # if trip_memo.driver_name:
                        #     trip_memo.driver_name.is_available = True
                        #     trip_memo.driver_name.save()

                # Serialize and return the updated TUR
                serializer = TruckUnloadingReportSerializer(tur)
                return Response({
                    'msg': "TruckUnloadingReport updated successfully.",
                    'status': 'success',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'msg': f"An error occurred: {str(e)}",
                'status': 'error',
                'data': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TURSoftDeleteAPIView(APIView):
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
            instance = TruckUnloadingReport.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'Truck Unloading Report deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except TruckUnloadingReport.DoesNotExist:
            return Response({
                'msg': 'Truck Unloading Report not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class TURPermanentDeleteAPIView(APIView):
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
            instance = TruckUnloadingReport.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'Truck Unloading Report permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except TruckUnloadingReport.DoesNotExist:
            return Response({
                'msg': 'Truck Unloading Report not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)



class GenerateLocalMemoDeliveryPDF(APIView):
    def get(self, request, memo_no):
        # Fetch the delivery details based on memo_no
        delivery = get_object_or_404(LocalMemoDelivery, memo_no=memo_no)
        bookings = delivery.lr_booking.all()

        # Fetch company details
        company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

        # Generate barcode for the memo_no
        barcode_base64 = generate_barcode(memo_no)

        # Get the logged-in user's name
        user_profile = UserProfile.objects.get(user=delivery.created_by)
        user_name = user_profile.first_name + " "+user_profile.last_name

        # Render HTML to string
        html_string = render(request, 'delivery/local_memo_delivery_pdf.html', {
            'company': company,
            'delivery': delivery,
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
        response['Content-Disposition'] = f'inline; filename=local_memo_{memo_no}.pdf'

        # Handle branch manager print status
        if request.user.userprofile.role == 'branch_manager':
            if delivery.printed_by_branch_manager:
                return Response({"msg": "This memo has already been printed by a branch manager.", 'status': 'error'}, status=400)
            delivery.printed_by_branch_manager = True
            delivery.save()

        return response

class GenerateLMDNumberView(APIView):
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
            last_booking_memo = LocalMemoDelivery.objects.filter(
                branch_name_id=branch_id,
                memo_no__startswith=prefix
            ).exclude(memo_no__isnull=True).exclude(memo_no__exact='').order_by('-memo_no').first()

            if last_booking_memo:
                last_sequence_number = int(last_booking_memo.memo_no[len(prefix):])
                new_memo_no = f"{prefix}{str(last_sequence_number + 1).zfill(5)}"
            else:
                new_memo_no = f"{prefix}00001"

            # On successful LR number generation
            response_data = {
                'msg': 'Memo number generated successfully',
                'status': 'success',
                'data': {
                    'memo_no': new_memo_no
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
                'message': 'An error occurred during Memo number generation due to invalid data.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any other unexpected exceptions
            response_data = {
                'status': 'error',
                'message': 'An error occurred while generating the Memo number.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CreateLDMView(APIView):    
    def post(self, request, *args, **kwargs):
        print(request.data)
        data = request.data
        lr_booking_ids = data.pop('lr_booking', [])
        requested_branch = data.get('branch_name')

        branch_id = request.data.get("branch_name")
        from_branch_id = request.data.get("from_branch")
        if branch_id != from_branch_id:
                return Response({
                    "status": "error",
                    "msg": "Login Branch and From Branch must be the same."
                }, status=status.HTTP_400_BAD_REQUEST)

        try:
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

                # Validation 1: Check TruckUnloadingReport completion
                tur_reports = TruckUnloadingReport.objects.filter(
                    tur_details__lr_booking=lr_booking,
                ).distinct()

                # Check if all related TruckUnloadingReports are inactive or flagged
                if not tur_reports.exists() or all(not tur.is_active or not tur.flag for tur in tur_reports):
                    return Response({
                        "message": f"LR_Bokking {lr_no}: All related TruckUnloadingReports are inactive or flagged or not any one TUR Created.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 2: Match to_branch and TruckUnloadingReport branch_name, and ensure is_active and flag are true
                valid_tur_reports = [
                    tur for tur in tur_reports 
                    if tur.is_active and tur.flag and lr_booking.to_branch_id == tur.branch_name_id
                ]

                if not valid_tur_reports:
                    return Response({
                        "message": f"LR_Bokking {lr_no}: No TruckUnloadingReport matches the LR_Bokking to_branch with active and non-flagged status, Means this lr last TUR not completed Properly",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 3: Check del_type is "LOCAL"
                if lr_booking.del_type_id != 1:  # Assuming 1 corresponds to "LOCAL"
                    return Response({
                        "message": f"LR_Bokking {lr_no}: Not a local delivery type.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validation 4: Match requested branch with to_branch
                if lr_booking.to_branch_id != requested_branch:
                    return Response({
                        "message": f"LR_Bokking {lr_no}: to_branch does not match requested branch.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

            # If all validations pass, proceed with transaction and creation
            with transaction.atomic():
                # Check for active deliveries (existing code)
                if lr_booking_ids:
                    lr_bookings_with_active_delivery = LR_Bokking.objects.filter(
                        lr_no__in=lr_booking_ids,
                        delivery_lr_bookings__is_active=True,
                        delivery_lr_bookings__flag=True
                    ).distinct()

                    if lr_bookings_with_active_delivery.exists():
                        active_lr_numbers = lr_bookings_with_active_delivery.values_list('lr_no', flat=True)
                        return Response({
                            "message": "Some LR_Bokking entries are already associated with an active local delivery memo.",
                            "status": "error",
                            "active_lr_numbers": list(active_lr_numbers)
                        }, status=status.HTTP_400_BAD_REQUEST)

                # Create the delivery object
                serializer = LocalMemoDeliverySerializer(data=data)
                if serializer.is_valid():
                    delivery = serializer.save()

                    if lr_booking_ids:
                        lr_bookings = LR_Bokking.objects.filter(lr_no__in=lr_booking_ids)

                        if len(lr_bookings) != len(lr_booking_ids):
                            raise ValueError("One or more LR_Booking IDs not found.")

                        delivery.lr_booking.set(lr_bookings)
                        delivery.created_by = request.user

                    response_serializer = LocalMemoDeliverySerializer(delivery)
                    return Response({
                        "message": "Local Delivery Memo created successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_201_CREATED)

                return Response({
                    "message": "Failed to create Local Delivery Memo",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({
                "message": str(e),
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "message": "An error occurred while creating Local Delivery Memo",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class LMDRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        standard_rate_id = request.data.get('id')

        # Check if 'id' is provided
        if not standard_rate_id:
            return Response({
                'message': 'Local Memo Delivery ID is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the StandardRate instance
            standard_rate = LocalMemoDelivery.objects.get(id=standard_rate_id)
        except LocalMemoDelivery.DoesNotExist:
            return Response({
                'message': 'Local Memo Delivery not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = LocalMemoDeliverySerializer(standard_rate)

        # Return the data with success status
        return Response({
            'message': 'Local Memo Delivery retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    
class LMDRetrieveAllView(APIView):
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
            items = LocalMemoDelivery.objects.filter(
                flag=True
                ).filter(
                Q(branch_name__in=allowed_branches)
                ).filter(
                Q(branch_name_id=branch_id)
                ).order_by('-id')

            # Serialize the items data
            serializer = LocalMemoDeliverySerializer(items, many=True)

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
    
class LMDRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter the queryset for active StandardRate instances
            queryset = LocalMemoDelivery.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = LocalMemoDeliverySerializer(queryset, many=True)

            # Prepare the response data
            response_data = {
                'msg': 'Local Memo Delivery retrieved successfully',
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

class LmdFilterView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(LocalMemoDelivery, filters)

            # Serialize the filtered data
            serializer = LocalMemoDeliverySerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class UpdateLDMView(APIView):  
    def post(self, request, *args, **kwargs):
        data = request.data
        lr_booking_ids = data.pop('lr_booking', [])
        requested_branch = data.get('branch_name')
        ldm_id = data.get('id')  

        if not ldm_id:
            return Response({
                'message': 'Local Memo Delivery ID is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        branch_id = request.data.get("branch_name")
        from_branch_id = request.data.get("from_branch")
        if branch_id != from_branch_id:
                return Response({
                    "status": "error",
                    "msg": "Login Branch and From Branch must be the same."
                }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the Local Delivery Memo instance
            try:
                delivery = LocalMemoDelivery.objects.get(id=ldm_id)
            except LocalMemoDelivery.DoesNotExist:
                return Response({
                    "message": f"Local Delivery Memo with ID {ldm_id} does not exist.",
                    "status": "error"
                }, status=status.HTTP_404_NOT_FOUND)

            # Validate each LR_Bokking in the requested list
            for lr_no in lr_booking_ids:
                try:
                    lr_booking = LR_Bokking.objects.get(lr_no=lr_no)
                except LR_Bokking.DoesNotExist:
                    return Response({
                        "message": f"LR_Bokking with lr_no {lr_no} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                 # Validation 1: Check TruckUnloadingReport completion
                tur_reports = TruckUnloadingReport.objects.filter(
                    tur_details__lr_booking=lr_booking
                ).distinct()

                # Check if all related TruckUnloadingReports are inactive or flagged
                if not tur_reports.exists() or all(not tur.is_active or not tur.flag for tur in tur_reports):
                    return Response({
                        "message": f"LR_Bokking {lr_no}: All related TruckUnloadingReports are inactive or flagged or not created.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 2: Match to_branch and TruckUnloadingReport branch_name
                valid_tur_reports = [
                    tur for tur in tur_reports
                    if tur.is_active and tur.flag and lr_booking.to_branch_id == tur.branch_name_id
                ]

                if not valid_tur_reports:
                    return Response({
                        "message": f"LR_Bokking {lr_no}: No TruckUnloadingReport matches the LR_Bokking to_branch with active and non-flagged status.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # # Validation 2: Match to_branch and TruckUnloadingReport branch_name
                # if lr_booking.to_branch_id != tur.branch_name_id:
                #     return Response({
                #         "message": f"LR_Bokking {lr_no}: to_branch does not match TruckUnloadingReport branch.",
                #         "status": "error"
                #     }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 3: Check del_type is "LOCAL"
                if lr_booking.del_type_id != 1:  # Assuming 1 corresponds to "LOCAL"
                    return Response({
                        "message": f"LR_Bokking {lr_no}: Not a local delivery type.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 4: Match requested branch with to_branch
                if lr_booking.to_branch_id != requested_branch:
                    return Response({
                        "message": f"LR_Bokking {lr_no}: to_branch does not match requested branch.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

            # If all validations pass, proceed with transaction and update
            with transaction.atomic():
                # Check for active deliveries
                if lr_booking_ids:
                    lr_bookings_with_active_delivery = LR_Bokking.objects.filter(
                        lr_no__in=lr_booking_ids,
                        delivery_lr_bookings__is_active=True,
                        delivery_lr_bookings__flag=True
                    ).exclude(delivery_lr_bookings=delivery).distinct()

                    if lr_bookings_with_active_delivery.exists():
                        active_lr_numbers = lr_bookings_with_active_delivery.values_list('lr_no', flat=True)
                        return Response({
                            "message": "Some LR_Bokking entries are already associated with another active local delivery memo.",
                            "status": "error",
                            "active_lr_numbers": list(active_lr_numbers)
                        }, status=status.HTTP_400_BAD_REQUEST)

                # Update the delivery object
                serializer = LocalMemoDeliverySerializer(delivery, data=data, partial=True)
                if serializer.is_valid():
                    updated_delivery = serializer.save(updated_by=request.user)

                    if lr_booking_ids:
                        lr_bookings = LR_Bokking.objects.filter(lr_no__in=lr_booking_ids)

                        if len(lr_bookings) != len(lr_booking_ids):
                            raise ValueError("One or more LR_Booking IDs not found.")

                        updated_delivery.lr_booking.set(lr_bookings)

                    response_serializer = LocalMemoDeliverySerializer(updated_delivery)
                    return Response({
                        "message": "Local Delivery Memo updated successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_200_OK)

                return Response({
                    "message": "Failed to update Local Delivery Memo",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response({
                "message": str(e),
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "message": "An error occurred while updating Local Delivery Memo",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class LMDSoftDeleteAPIView(APIView):
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
            instance = LocalMemoDelivery.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'Local Memo Delivery deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except LocalMemoDelivery.DoesNotExist:
            return Response({
                'msg': 'Local Memo Delivery not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class LMDPermanentDeleteAPIView(APIView):
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
            instance = LocalMemoDelivery.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'Local Memo Delivery permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except LocalMemoDelivery.DoesNotExist:
            return Response({
                'msg': 'Local Memo Delivery not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)



class GenerateDSNumberViews(APIView):   
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
            last_booking_memo = DeliveryStatement.objects.filter(
                branch_name_id=branch_id,
                delivery_no__startswith=prefix
            ).exclude(delivery_no__isnull=True).exclude(delivery_no__exact='').order_by('-delivery_no').first()

            if last_booking_memo:
                last_sequence_number = int(last_booking_memo.delivery_no[len(prefix):])
                new_delivery_no = f"{prefix}{str(last_sequence_number + 1).zfill(5)}"
            else:
                new_delivery_no = f"{prefix}00001"

            # On successful LR number generation
            response_data = {
                'msg': 'DS number generated successfully',
                'status': 'success',
                'data': {
                    'memo_no': new_delivery_no
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
                'message': 'An error occurred during DS number generation due to invalid data.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any other unexpected exceptions
            response_data = {
                'status': 'error',
                'message': 'An error occurred while generating the DS number.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateDeliveryStatementPDF(APIView):
    def get(self, request, delivery_no):
        # Fetch the statement details based on delivery_no
        statement = get_object_or_404(DeliveryStatement, delivery_no=delivery_no)
        bookings = statement.lr_booking.all()

        # Fetch company details
        company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

        # Generate barcode for the delivery_no
        barcode_base64 = generate_barcode(delivery_no)

        # Get the logged-in user's name
        user_profile = UserProfile.objects.get(user=statement.created_by)
        user_name = user_profile.first_name + " "+user_profile.last_name

        # Render HTML to string
        html_string = render(request, 'statements/delivery_statement_pdf.html', {
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
        response['Content-Disposition'] = f'inline; filename=delivery_statement_{delivery_no}.pdf'

        # Handle branch manager print status
        if request.user.userprofile.role == 'branch_manager':
            if statement.printed_by_branch_manager:
                return Response({"msg": "This statement has already been printed by a branch manager.", 'status': 'error'}, status=400)
            statement.printed_by_branch_manager = True
            statement.save()

        return response

class CreateDeliveryStatementView(APIView): 
    def post(self, request, *args, **kwargs):
        data = request.data
        lr_booking_ids = data.pop('lr_booking', [])
        requested_branch = data.get('branch_name')

        try:
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

                # Validation 1: Check if LR_Bokking's to_branch matches requested branch
                if lr_booking.to_branch_id != requested_branch:
                    return Response({
                        "message": f"LR_Bokking {lr_no}: to_branch does not match requested branch.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 2: Check TruckUnloadingReport details
                tur_details = TruckUnloadingReportDetails.objects.filter(
                    lr_booking=lr_booking
                ).prefetch_related('truckunloadingreport_set')

                # Check if there are related TruckUnloadingReport instances with is_active=True and flag=True
                valid_tur = False  # Default value to indicate no valid records
                for detail in tur_details:
                    # Check related TruckUnloadingReport records
                    if detail.truckunloadingreport_set.filter(is_active=True, flag=True).exists():
                        valid_tur = True
                        break  # Exit loop early if a valid record is found

                if not valid_tur:
                    return Response({
                        "message": f"LR_Bokking {lr_no}:  TruckUnloadingReport Not completed or TruckUnloadingReport details not found.",
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
                        "message": f"LR_Bokking {lr_no}: TruckUnloadingReport's branch does not match with lr_booking to_branch. Means all TruckUnloadingReport not completed for this lr_booking.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 3: Check if del_type is LOCAL and validate LocalMemoDelivery
                if lr_booking.del_type_id == 1:  # Assuming 1 corresponds to "LOCAL"
                    local_memo_deliveries = LocalMemoDelivery.objects.filter(
                        lr_booking=lr_booking,
                        is_active=True,
                        flag=True
                    )
                    if not local_memo_deliveries.exists():
                        return Response({
                            "message": f"LR_Bokking {lr_no}: LocalMemoDelivery is not completed for local delivery type.",
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # # Additional validation for pay_type_id == 1
                # if lr_booking.pay_type_id == 2:  # Assuming 1 corresponds to "ToPAY"
                #      # Check in VoucherReceiptBranch
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

                #     # If not present in either model
                #     if not (exists_in_voucher_receipt_branch or exists_in_money_receipt):
                #         return Response({
                #             "message": f"LR Booking with id {lr_booking.lr_no} has pay_type_id=1 (ToPAY) but is not linked with any active VoucherReceiptBranch or MoneyReceipt.",
                #             "status": "error"
                #         }, status=status.HTTP_400_BAD_REQUEST)

            # If all validations pass, proceed with creation
            with transaction.atomic():
                # Validate and process each LR_Bokking
                for lr_no in lr_booking_ids:
                    try:
                        lr_booking = LR_Bokking.objects.get(lr_no=lr_no)
                    except LR_Bokking.DoesNotExist:
                        raise ValueError(f"LR_Bokking with lr_no {lr_no} does not exist.")                    

                    if lr_booking.pay_type_id == 2:  # "ToPAY"
                        exists_in_voucher_receipt_branch = VoucherReceiptBranch.objects.filter(
                            lr_booking=lr_booking, is_active=True, flag=True
                        ).exists()
                        exists_in_money_receipt = MoneyReceipt.objects.filter(
                            lr_booking=lr_booking, is_active=True, flag=True
                        ).exists()

                        if not (exists_in_voucher_receipt_branch or exists_in_money_receipt):
                            billing_party = lr_booking.billing_party
                            if not billing_party:
                                raise ValueError(f"LR_Bokking {lr_no}: Billing Party is missing.")
                            
                            
                            # Check or create CustomerOutstanding
                            outstanding_record, created = CustomerOutstanding.objects.get_or_create(
                                billing_party=billing_party,
                                defaults={
                                    'credit_amount': billing_party.credit_amount,
                                    'credit_period': billing_party.credit_period,
                                    'last_credit_date': timezone.now().date() 
                                    }
                            )
                            
                            # Validate credit period
                            if not billing_party.credit_period:  # This will check if it's None or blank
                                raise ValueError(
                                    f"Invalid credit period for Billing Party {billing_party}. Credit period cannot be null or blank."
                                )
                            if not billing_party.credit_amount:  # This will check if it's None or blank
                                raise ValueError(
                                    f"Invalid credit amount for Billing Party {billing_party}. Credit period cannot be null or blank."
                                )
                            
                            if billing_party.credit_period < 0:
                                raise ValueError(
                                    f"Invalid credit period for Billing Party {billing_party}. Credit period cannot be less than 0."
                                )
                            
                            if not created:
                                # Check credit period against billing_party's credit_period
                                if outstanding_record.last_credit_date:
                                    last_credit_date = outstanding_record.last_credit_date
                                    current_date = timezone.now().date()

                                    # Calculate the difference in days
                                    days_diff = (current_date - last_credit_date).days                                    
                                    if days_diff > billing_party.credit_period:
                                        raise ValueError(
                                            f"Credit period expired or invalid for Billing Party {billing_party}. "
                                            "Please make payment to proceed."
                                        )                            
                            # Validate credit limits
                            total_grand_total = sum(
                                [booking.grand_total for booking in outstanding_record.lr_booking.all()]
                            ) + lr_booking.grand_total

                            if total_grand_total > billing_party.credit_amount:
                                raise ValueError(
                                    f"Credit limit exceeded for Billing Party {billing_party}. "
                                    "Please make payment to proceed."
                                )                            

                            # Add lr_booking to CustomerOutstanding
                            if not created:
                                outstanding_record.lr_booking.add(lr_booking)
                            else:
                                outstanding_record.lr_booking.set([lr_booking])

                            outstanding_record.save()

                serializer = DeliveryStatementSerializer(data=data)
                if serializer.is_valid():
                    delivery_statement = serializer.save()

                    # Add LR_Bokking entries to the ManyToMany field
                    lr_bookings = LR_Bokking.objects.filter(lr_no__in=lr_booking_ids)
                    if len(lr_bookings) != len(lr_booking_ids):
                        raise ValueError("One or more LR_Booking IDs not found.")
                    delivery_statement.lr_booking.set(lr_bookings)
                    delivery_statement.created_by = request.user
                    

                    try :
                        # Send emails to consignors and consignees
                        recipient_list = []  # List to store valid email addresses
                        pdf_sent = True

                        # Loop through each LR_Bokking object to get consignor and consignee emails
                        for lr_booking in lr_bookings:
                            # Extract consignor and consignee emails
                            consignor_email = lr_booking.consignor.email_id.strip() if lr_booking.consignor else None
                            consignee_email = lr_booking.consignee.email_id.strip() if lr_booking.consignee else None

                            # Validate and add to recipient list
                            for email in [consignor_email, consignee_email]:
                                if email:
                                    try:
                                        validate_email(email)
                                        recipient_list.append(email)
                                    except ValidationError:
                                        continue  # Ignore invalid email addresses

                        # Generate PDF
                        lr_no = delivery_statement.delivery_no
                        pdf_response = GenerateDeliveryStatementPDF().get(request, lr_no)
                        pdf_path = f"/tmp/invoice_{lr_no}.pdf"
                        with open(pdf_path, 'wb') as pdf_file:
                            pdf_file.write(pdf_response.content)


                        # Send email if there are valid recipients
                        if recipient_list:
                            subject = "Delivery Statement Done"
                            message = "A new delivery statement has been created which is associated with your LR booking."
                            send_email_with_attachment(
                                subject,
                                message,                            
                                recipient_list, 
                                pdf_path                            
                            )
                        # Remove temporary PDF file
                        os.remove(pdf_path)
                    except Exception as email_error:
                        pdf_sent = False
                        # Log or handle the error if needed
                        print(f"Failed to send email or generate PDF: {str(email_error)}")

                    response_serializer = DeliveryStatementSerializer(delivery_statement)
                    if pdf_sent:
                        return Response({
                            "message": "Delivery Statement created successfully!",
                            "status": "success",
                            "data": response_serializer.data
                        }, status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                            "message": "Delivery Statement created successfully, but failed to send email.",
                            "status": "success",
                            "data": response_serializer.data
                        }, status=status.HTTP_201_CREATED)
                    
                return Response({
                    "message": "Failed to create Delivery Statement",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "message": "An error occurred while creating Delivery Statement",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class DSRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        standard_rate_id = request.data.get('id')

        # Check if 'id' is provided
        if not standard_rate_id:
            return Response({
                'message': 'Delivery Statement ID is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the StandardRate instance
            standard_rate = DeliveryStatement.objects.get(id=standard_rate_id)
        except DeliveryStatement.DoesNotExist:
            return Response({
                'message': 'Delivery Statement not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = DeliveryStatementSerializer(standard_rate)

        # Return the data with success status
        return Response({
            'message': 'Delivery Statement retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    
class DSRetrieveAllView(APIView):
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
            items = DeliveryStatement.objects.filter(
                flag=True
                ).filter(
                Q(branch_name__in=allowed_branches)
                ).filter(
                Q(branch_name_id=branch_id)
                ).order_by('-id')

            # Serialize the items data
            serializer = DeliveryStatementSerializer(items, many=True)

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
    
class DSRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter the queryset for active StandardRate instances
            queryset = DeliveryStatement.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = DeliveryStatementSerializer(queryset, many=True)

            # Prepare the response data
            response_data = {
                'msg': 'Delivery Statement retrieved successfully',
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

class DSFilterView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(DeliveryStatement, filters)

            # Serialize the filtered data
            serializer = DeliveryStatementSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class UpdateDeliveryStatementView(APIView):  
    def post(self, request, *args, **kwargs):
        data = request.data
        delivery_statement_id = data.get('id')
        lr_booking_ids = data.pop('lr_booking', [])
        requested_branch = data.get('branch_name')

        try:
            if not delivery_statement_id:
                return Response({
                    'message': 'delivery statement ID is required',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                delivery_statement = DeliveryStatement.objects.get(id=delivery_statement_id)
            except DeliveryStatement.DoesNotExist:
                return Response({
                    "message": f"DeliveryStatement with id {delivery_statement_id} does not exist.",
                    "status": "error"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate each LR_Booking in the requested list
            for lr_no in lr_booking_ids:
                # Get the LR_Booking object
                try:
                    lr_booking = LR_Bokking.objects.get(lr_no=lr_no)
                except LR_Bokking.DoesNotExist:
                    return Response({
                        "message": f"LR_Booking with lr_no {lr_no} does not exist.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 1: Check if LR_Booking's to_branch matches requested branch
                if lr_booking.to_branch_id != requested_branch:
                    return Response({
                        "message": f"LR_Booking {lr_no}: to_branch does not match requested branch.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 2: Check TruckUnloadingReport details
                tur_details = TruckUnloadingReportDetails.objects.filter(
                    lr_booking=lr_booking
                ).prefetch_related('truckunloadingreport_set')

                # Check if there are related TruckUnloadingReport instances with is_active=True and flag=True
                valid_tur = False  # Default value to indicate no valid records
                for detail in tur_details:
                    # Check related TruckUnloadingReport records
                    if detail.truckunloadingreport_set.filter(is_active=True, flag=True).exists():
                        valid_tur = True
                        break  # Exit loop early if a valid record is found

                if not valid_tur:
                    return Response({
                        "message": f"LR_Bokking {lr_no}:  TruckUnloadingReport Not completed or TruckUnloadingReport details not found.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                valid_branch = False
                print("TUR Details",tur_details)
                for tur_detail in tur_details:                   
                    truck_unloading_reports = tur_detail.truckunloadingreport_set.filter(
                        is_active=True,
                        flag=True
                    )                   
                    if any(tur.branch_name_id == lr_booking.to_branch_id for tur in truck_unloading_reports):
                        valid_branch = True
                        break
                print("valid branch",valid_branch)
                if not valid_branch:
                    return Response({
                        "message": f"LR_Bokking {lr_no}: TruckUnloadingReport's branch does not match with lr_booking to_branch. Means all TruckUnloadingReport not completed for this lr_booking.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Validation 3: Check if del_type is LOCAL and validate LocalMemoDelivery
                if lr_booking.del_type_id == 1:  # Assuming 1 corresponds to "LOCAL"
                    local_memo_deliveries = LocalMemoDelivery.objects.filter(
                        lr_booking=lr_booking,
                        is_active=True,
                        flag=True
                    )
                    if not local_memo_deliveries.exists():
                        return Response({
                            "message": f"LR_Booking {lr_no}: LocalMemoDelivery is not completed for local delivery type.",
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                # # Additional validation for pay_type_id == 1
                # if lr_booking.pay_type_id == 2:  # Assuming 1 corresponds to "ToPAY"
                #      # Check in VoucherReceiptBranch
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

                #     # If not present in either model
                #     if not (exists_in_voucher_receipt_branch or exists_in_money_receipt):
                #         return Response({
                #             "message": f"LR Booking with id {lr_booking.lr_no} has pay_type_id=1 (ToPAY) but is not linked with any active VoucherReceiptBranch or MoneyReceipt.",
                #             "status": "error"
                #         }, status=status.HTTP_400_BAD_REQUEST)

            # If all validations pass, proceed with the update
            with transaction.atomic():
                serializer = DeliveryStatementSerializer(delivery_statement, data=data, partial=True)
                if serializer.is_valid():
                    delivery_statement = serializer.save(updated_by=request.user)

                    # Update the ManyToMany field with the new LR_Booking entries
                    lr_bookings = LR_Bokking.objects.filter(lr_no__in=lr_booking_ids)
                    if len(lr_bookings) != len(lr_booking_ids):
                        raise ValueError("One or more LR_Booking IDs not found.")
                    delivery_statement.lr_booking.set(lr_bookings)

                    response_serializer = DeliveryStatementSerializer(delivery_statement)
                    return Response({
                        "message": "Delivery Statement updated successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_200_OK)

                return Response({
                    "message": "Failed to update Delivery Statement",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "message": "An error occurred while updating Delivery Statement",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class DSSoftDeleteAPIView(APIView):
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
            instance = DeliveryStatement.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'StandardRate deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except DeliveryStatement.DoesNotExist:
            return Response({
                'msg': 'StandardRate not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class DSPermanentDeleteAPIView(APIView):
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
            instance = DeliveryStatement.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'StandardRate permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except DeliveryStatement.DoesNotExist:
            return Response({
                'msg': 'StandardRate not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)


class CustomerOutstandingPendencyReport(APIView):
    def post(self, request, *args, **kwargs):
        # Get 'billing_party' from POST data
        billing_party_id = request.data.get('billing_party')

        # Check if 'billing_party' is provided
        if billing_party_id:
            # Filter by billing_party if provided
            queryset = CustomerOutstanding.objects.filter(billing_party_id=billing_party_id)

            # Check if any results are found
            if not queryset.exists():
                return Response({
                    'message': 'This billing party does not have any pending bill',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Retrieve all records if no billing_party is provided
            queryset = CustomerOutstanding.objects.all()

        # Serialize the retrieved instances
        serializer = CustomerOutstandingSerializer(queryset, many=True)

        # Return the data with success status
        return Response({
            'message': 'Customer Outstanding Pendency Report retrieved successfully',
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
