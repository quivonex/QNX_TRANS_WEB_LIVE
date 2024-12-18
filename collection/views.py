from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import BookingMemo, BookingMemoLRs, Collection,LR_Bokking,TripMode,TripMemo,TripBokkingMemos,BrokerMasterTrips,BrokerMaster
from .serializers import BookingMemoLRsSerializer, BookingMemoSerializer, CollectionSerializer,LRBokkingSerializer,TripMemoSerializer,TripBokkingMemosSerializer,TripModeSerializer,BrokerMasterTripsSerializer,BrokerMasterSerializer
from rest_framework.permissions import AllowAny
from django.db import transaction
from branches.models import BranchMaster
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import LR_Bokking,VehicalHireContract
from .serializers import LRBokkingSerializer,VehicalHireContractSerializer
from transactions.models import LoadTypes, PaidTypes, PayTypes, CollectionTypes, DeliveryTypes
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from company.models import CompanyMaster
from delivery.models import TruckUnloadingReport
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import base64
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from weasyprint import HTML, CSS
from django.views.decorators.csrf import csrf_exempt
import json
from users.models import UserProfile
from rest_framework.exceptions import ValidationError
from company.filters import apply_filters
from account.models import VoucherReceiptBranch,MoneyReceipt
from vehicals.models import VehicalMaster,DriverMaster
from django.db.models import Q
import re

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

class GenerateCollectionPDF(APIView):       
    def get(self, request, memo_no):
        # Fetch the collection details based on memo_no
        collection = get_object_or_404(Collection, memo_no=memo_no)
        lrs = collection.lr_booking.all()

        # Optionally fetch company details if needed for the invoice
        company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

        # Generate barcode for the memo_no  
        barcode_base64 = generate_barcode(memo_no)

        # Get the logged-in user's name
        user_profile = UserProfile.objects.get(user=collection.created_by)
        user_name = user_profile.first_name + " "+user_profile.last_name

        # Render HTML to string using your collection data
        html_string = render(request, 'collection/collection_pdf.html', {
            'company': company,
            'collection': collection,
            'lrs': lrs,
            'barcode_base64': barcode_base64,  # Pass the barcode to the template
            'user_name': user_name,  # Pass the user's name to the template
        }).content.decode('utf-8')

        # Define CSS for styling (page size: Legal)
        css = CSS(string=''' 
            @page {
                size: legal;
                margin: 5mm;
            }
        ''')

        # Convert the HTML into a PDF document using WeasyPrint
        html = HTML(string=html_string)
        pdf = html.write_pdf(stylesheets=[css])

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=collection_{memo_no}.pdf'

        user_profile = request.user.userprofile
        # Check if the user is a branch manager and if already printed
        if user_profile.role == 'branch_manager':
            if collection.printed_by_branch_manager:
                return Response({"msg": "Invoice has already been printed by a branch manager.",'status': 'error'}, status=400)
            collection.printed_by_branch_manager = True
            collection.save()

        return response

def generate_collection_pdf(request, memo_no):
    print(memo_no)
    # Fetch the collection details based on memo_no
    collection = get_object_or_404(Collection, memo_no=memo_no)
    lrs = collection.lr_booking.all()

    # Optionally fetch company details if needed for the invoice
    company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

    # Generate barcode for the memo_no  
    barcode_base64 = generate_barcode(memo_no)

    # Render HTML to string using your collection data
    html_string = render(request, 'collection/collection_pdf.html', {
        'company': company,
        'collection': collection,
        'lrs':lrs,
        'barcode_base64': barcode_base64,  # Pass the barcode to the template
    }).content.decode('utf-8')

    # Define CSS for styling (page size: Legal)
    css = CSS(string='''
        @page {
            size: legal;
            margin: 5mm;
        }
    ''')

    # Convert the HTML into a PDF document using WeasyPrint
    html = HTML(string=html_string)
    pdf = html.write_pdf(stylesheets=[css])

    # Return PDF response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename=collection_{memo_no}.pdf'
    return response

class GenerateCollectionMemo(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)

            # Extract the HTML content and memo number
            html_content = data.get('html')
            memo_no = data.get('memo_no')

            # Validate input
            if not html_content or not memo_no:
                return JsonResponse({'error': 'HTML content or memo number missing'}, status=400)

            # Fetch dynamic data based on memo number
            company = get_object_or_404(CompanyMaster, flag=True, is_active=True)
            collection = get_object_or_404(Collection, memo_no=memo_no)            
            # Generate dynamic data placeholders
            barcode_base64 = generate_barcode(memo_no)

            user_name = request.user.get_full_name() or request.user.username

            # Replace placeholders in the HTML content with actual dynamic data
            company_logo_url = request.build_absolute_uri(company.company_logo.url)
            html_content = html_content.replace('{{ company.company_logo }}', company_logo_url)
            html_content = html_content.replace('{{ company.address }}', company.address)
            html_content = html_content.replace('{{ company.contact_number }}', company.contact_number)
            html_content = html_content.replace('{{ barcode_base64 }}', barcode_base64)
            html_content = html_content.replace('{{ collection.memo_no }}', str(collection.memo_no))
            html_content = html_content.replace('{{ collection.date }}', collection.date.strftime('%Y-%m-%d'))
            html_content = html_content.replace('{{ collection.from_branch }}', str(collection.from_branch))
            html_content = html_content.replace('{{ collection.driver_name }}', str(collection.driver_name))
            html_content = html_content.replace('{{ collection.branch_name }}', str(collection.branch_name))
            html_content = html_content.replace('{{ collection.vehical_no }}', str(collection.vehical_no.vehical_number))
            html_content = html_content.replace('{{ collection.vehical_no.owner.name }}', str(collection.vehical_no.owner.name))
            html_content = html_content.replace('{{ collection.vehical_no.vehical_type.type_name }}', str(collection.vehical_no.vehical_type.type_name))
            html_content = html_content.replace('{{ collection.contact }}', str(collection.contact))
            html_content = html_content.replace('{{ collection.memo_remarks }}', str(collection.memo_remarks ))
            html_content = html_content.replace('{{ collection.balance }}', str(collection.balance  ))
            html_content = html_content.replace('{{ collection.extra_amt }}', str(collection.extra_amt   ))
            html_content = html_content.replace('{{ collection.advance }}', str(collection.advance   ))
            html_content = html_content.replace('{{ collection.hamali }}', str(collection.hamali    ))
            html_content = html_content.replace('{{ collection.total_amt }}', str(collection.total_amt    ))
            html_content = html_content.replace('{{ user_name }}', str(user_name))
           

            # Define custom CSS for the page layout
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
            response['Content-Disposition'] = f'inline; filename=collection_memo_{memo_no}.pdf'
            return response

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class GenerateCollectionNumberView(APIView):
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

            # Get the last non-null and non-blank collection number for this branch with matching prefix
            last_collection = Collection.objects.filter(
                branch_name_id=branch_id,
                memo_no__startswith=prefix
            ).exclude(memo_no__isnull=True).exclude(memo_no__exact='').order_by('-memo_no').first()

            if last_collection:
                last_sequence_number = int(last_collection.memo_no[len(prefix):])
                new_memo_no = f"{prefix}{str(last_sequence_number + 1).zfill(5)}"
            else:
                new_memo_no = f"{prefix}00001"

            # On successful collection number generation
            response_data = {
                'msg': 'Collection number generated successfully',
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
            # Handle cases where collection number conversion fails or other value-related errors occur
            response_data = {
                'status': 'error',
                'message': 'An error occurred during Collection number generation due to invalid data.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any other unexpected exceptions
            response_data = {
                'status': 'error',
                'message': 'An error occurred while generating the Collection number.',
                'error': str(e)
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CollectionGetCreateView(APIView):
    def post(self, request, *args, **kwargs):
        branch_id = request.data.get('branch_id')

        if branch_id is None:
            return Response({
                "message": "Branch ID is required.",
                "status": "error",
                "data": []  # Include empty data for consistency
            }, status=status.HTTP_400_BAD_REQUEST)

        # Filter LR_Bokking based on branch_id and coll_type = 1
        lr_bookings = LR_Bokking.objects.filter(
            branch_id=branch_id,
            coll_type=1
        )

        if not lr_bookings.exists():
            return Response({
                "message": "No LR bookings found for the provided branch ID and collection type.",
                "status": "error",
                "data": []  # Include empty data for consistency
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the filtered objects
        serializer = LRBokkingSerializer(lr_bookings, many=True)

        return Response({
            "message": "LR bookings fetched successfully!",
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class CreateCollectionView(APIView):    
    def post(self, request, *args, **kwargs):      
        data = request.data
        lr_booking_ids = data.pop('lr_booking', [])
        requested_branch = data.get('from_branch')

        branch_id = request.data.get("branch_name")
        from_branch_id = request.data.get("from_branch")
        if branch_id != from_branch_id:
                return Response({
                    "status": "error",
                    "msg": "Login Branch and From Branch must be the same."
                }, status=status.HTTP_400_BAD_REQUEST)

        # Wrap everything in a transaction
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

                # Validation 1: Check if LR_Bokking's from_branch matches requested branch
                if lr_booking.from_branch_id != requested_branch:
                    return Response({
                        "message": f"LR_Bokking {lr_no}: from_branch does not match requested From_branch.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 2: Check if coll_type is LOCAL and validate LocalMemoDelivery
                if lr_booking.coll_type_id != 1:  # Assuming 1 corresponds to "LOCAL"
                    return Response({
                        "message": f"LR_Bokking {lr_no}: Not a local Collection type.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)


            with transaction.atomic():

                # Check if any of the provided LR_Bokking instances are already part of an active collection
                if lr_booking_ids:
                    # Find any LR_Bokking instances that are associated with an active collection
                    lr_bookings_with_active_collection = LR_Bokking.objects.filter(
                        lr_no__in=lr_booking_ids,
                        collections_lr_bookings__is_active=True,
                        collections_lr_bookings__flag=True
                    ).distinct()

                    # If any LR_Bokking has an active collection, return an error
                    if lr_bookings_with_active_collection.exists():
                        active_lr_numbers = lr_bookings_with_active_collection.values_list('lr_no', flat=True)
                        return Response({
                            "message": "Some LR_Bokking entries are already associated with an active collection.",
                            "status": "error",
                            "active_lr_numbers": list(active_lr_numbers)  # Provide the LR numbers that are invalid
                        }, status=status.HTTP_400_BAD_REQUEST)

                # Create the Collection object
                serializer = CollectionSerializer(data=data)
                if serializer.is_valid():
                    collection = serializer.save()

                    # Now associate lr_booking instances with this collection
                    if lr_booking_ids:
                        lr_bookings = LR_Bokking.objects.filter(lr_no__in=lr_booking_ids)

                        # Ensure the number of found LR_Bookings matches the requested ids
                        if len(lr_bookings) != len(lr_booking_ids):
                            raise ValueError("One or more LR_Booking IDs not found.")

                        collection.lr_booking.set(lr_bookings)  # Set the M2M relationship
                        collection.created_by = request.user

                    # Re-serialize to return the full response with nested lr_booking details
                    response_serializer = CollectionSerializer(collection)
                    return Response({
                        "message": "Collection created successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_201_CREATED)

                return Response({
                    "message": "Failed to create collection",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "message": "An error occurred while creating collection",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class CollectionRetrieveView(APIView):
    permission_classes = [AllowAny]  # Adjust if authentication is needed

    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        effect_type_id = request.data.get('id')
        
        if not effect_type_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the CollectionEffectTypes instance
            instance = Collection.objects.get(pk=effect_type_id)
            serializer = CollectionSerializer(instance)

            print(serializer.data)
            
            response_data = {
                'msg': 'Collection type retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Collection.DoesNotExist:
            return Response({
                'msg': 'Collection type not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class CollectionRetrieveAllView(APIView):    
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


            # Retrieve all instances of Collection
            instances = Collection.objects.filter(flag=True                                                
            ).filter(
                Q(branch_name__in=allowed_branches) | Q(from_branch__in=allowed_branches)  
            ).filter(
                Q(branch_name_id=branch_id) | Q(from_branch_id=branch_id)
            ).order_by('-id')
            serializer = CollectionSerializer(instances, many=True)
            
            response_data = {
                'msg': 'Collection types retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving Collection Types.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class CollectionRetrieveFilteredView(APIView):
    permission_classes = [AllowAny]  # Adjust if authentication is needed

    def post(self, request, *args, **kwargs):
        try:
            # Extract filter value for is_active from request data
            is_active = request.data.get('is_active', True)  # Default to True if not provided
            
            # Filter instances based on is_active value
            queryset = Collection.objects.filter(is_active=is_active,flag=True).order_by('-id')
            serializer = CollectionSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'Collection types retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving Effect Types.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CollectionFilterView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(Collection, filters)

            # Serialize the filtered data
            serializer = CollectionSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class CollectionUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        data = request.data
        lr_booking_ids = data.pop('lr_booking', [])
        collection_id = request.data.get('id')
        requested_branch = data.get('from_branch')

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

                # Validation 1: Check if LR_Bokking's from_branch matches requested branch
                if lr_booking.from_branch_id != requested_branch:
                    return Response({
                        "message": f"LR_Bokking {lr_no}: from_branch does not match requested branch.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validation 2: Check if coll_type is LOCAL and validate LocalMemoDelivery
                if lr_booking.coll_type_id != 1:  # Assuming 1 corresponds to "LOCAL"
                    return Response({
                        "message": f"LR_Bokking {lr_no}: Not a local Collection type.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            with transaction.atomic():
                # Fetch the existing collection by ID
                collection = Collection.objects.get(pk=collection_id)

                # Get the current lr_booking IDs associated with the collection
                current_lr_booking_ids = set(collection.lr_booking.values_list('lr_no', flat=True))

                # New LR_Bokking entries to validate (exclude existing ones)
                new_lr_booking_ids = set(lr_booking_ids) - current_lr_booking_ids

                # Validation: Check if any of the new LR_Bokking instances are already in an active collection
                if new_lr_booking_ids:
                    # Find any LR_Bokking instances that are associated with an active collection
                    lr_bookings_with_active_collection = LR_Bokking.objects.filter(
                        lr_no__in=new_lr_booking_ids,
                        collections_lr_bookings__is_active=True,
                        collections_lr_bookings__flag=True
                    ).distinct()

                    # If any LR_Bokking has an active collection, return an error
                    if lr_bookings_with_active_collection.exists():
                        active_lr_numbers = lr_bookings_with_active_collection.values_list('lr_no', flat=True)
                        return Response({
                            "message": "Some LR_Bokking entries are already associated with an active collection.",
                            "status": "error",
                            "active_lr_numbers": list(active_lr_numbers)  # Provide the LR numbers that are invalid
                        }, status=status.HTTP_400_BAD_REQUEST)


                # Update the Collection fields (except lr_booking)
                serializer = CollectionSerializer(collection, data=data, partial=True)
                if serializer.is_valid():
                    collection = serializer.save(updated_by=request.user)

                    # Handle lr_booking: Add new ones and remove missing ones
                    if not lr_booking_ids:
                        collection.lr_booking.clear()
                    else:
                        lr_bookings = LR_Bokking.objects.filter(lr_no__in=lr_booking_ids)

                        # Ensure the number of found LR_Bookings matches the requested ids
                        if len(lr_bookings) != len(lr_booking_ids):
                            raise ValueError("One or more LR_Booking IDs not found.")

                        # Get existing lr_booking set for the collection
                        current_lr_bookings = set(collection.lr_booking.all())

                        # Convert new lr_booking_ids into queryset
                        new_lr_bookings = set(lr_bookings)

                        # Find the ones to add (new_lr_bookings - current_lr_bookings)
                        to_add = new_lr_bookings - current_lr_bookings

                        # Find the ones to remove (current_lr_bookings - new_lr_bookings)
                        to_remove = current_lr_bookings - new_lr_bookings

                        # Perform add and remove operations
                        if to_add:
                            collection.lr_booking.add(*to_add)
                        if to_remove:
                            collection.lr_booking.remove(*to_remove)

                    # Re-serialize to return the updated response with nested lr_booking details
                    response_serializer = CollectionSerializer(collection)
                    return Response({
                        "message": "Collection updated successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_200_OK)

                return Response({
                    "message": "Failed to update collection",
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Collection.DoesNotExist:
            return Response({
                "message": "Collection not found",
                "status": "error",
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "message": "An error occurred while updating collection",
                "status": "error",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class CollectionSoftDeleteAPIView(APIView):
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
            # Retrieve the Collection instance
            instance = Collection.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'Collection deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except Collection.DoesNotExist:
            return Response({
                'msg': 'Collection not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class CollectionPermanentDeleteAPIView(APIView):
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
            # Retrieve the Collection instance
            instance = Collection.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'Collection permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except Collection.DoesNotExist:
            return Response({
                'msg': 'Collection not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)



class CreateBookingMemoLRsView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Get data from the request
            serializer = BookingMemoLRsSerializer(data=request.data, context={'request': request})
            
            # Validate the incoming data
            if serializer.is_valid():
                # Save the collection
                collection = serializer.save(created_by=request.user)
                
                # Return success message and the created collection data
                return Response({
                    'status': 'success',
                    'message': 'BookingMemoLRs created successfully.',
                    'data': [BookingMemoLRsSerializer(collection).data]
                }, status=status.HTTP_201_CREATED)
            else:
                # Return validation errors
                return Response({
                    'message': 'Invalid data',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Catch and return any exceptions
            return Response({
                'message': 'An error occurred while creating the BookingMemoLRs.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BookingMemoLRsRetrieveView(APIView):    

    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        effect_type_id = request.data.get('id')
        
        if not effect_type_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the BookingMemoLRs instance
            instance = BookingMemoLRs.objects.get(pk=effect_type_id)
            serializer = BookingMemoLRsSerializer(instance)
            
            response_data = {
                'msg': 'BookingMemoLRs type retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Collection.DoesNotExist:
            return Response({
                'msg': 'BookingMemoLRs type not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class BookingMemoLRsRetrieveAllView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of BookingMemoLRs
            instances = BookingMemoLRs.objects.filter(flag=True).order_by('-id')

            serializer = BookingMemoLRsSerializer(instances, many=True)
            
            response_data = {
                'msg': 'BookingMemoLRs types retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving BookingMemoLRs.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BookingMemoLRsRetrieveFilteredView(APIView):   

    def post(self, request, *args, **kwargs):
        try:
            # Extract filter value for is_active from request data
            is_active = request.data.get('is_active', True)  # Default to True if not provided
            
            # Filter instances based on is_active value
            queryset = BookingMemoLRs.objects.filter(is_active=is_active,flag=True).order_by('-id')
            serializer = BookingMemoLRsSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'BookingMemoLRs retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving BookingMemoLRs.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BookingMemoLRsUpdateAPIView(APIView):
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
            # Retrieve the BookingMemoLRs instance
            instance = BookingMemoLRs.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = BookingMemoLRsSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'BookingMemoLRs updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update BookingMemoLRs',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except BookingMemoLRs.DoesNotExist:
            return Response({
                'msg': 'BookingMemoLRs not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BookingMemoLRsSoftDeleteAPIView(APIView):
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
            # Retrieve the BookingMemoLRs instance
            instance = BookingMemoLRs.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'BookingMemoLRs deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except BookingMemoLRs.DoesNotExist:
            return Response({
                'msg': 'BookingMemoLRs not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class BookingMemoLRsPermanentDeleteAPIView(APIView):
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
            # Retrieve the BookingMemoLRs instance
            instance = BookingMemoLRs.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'BookingMemoLRs permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except BookingMemoLRs.DoesNotExist:
            return Response({
                'msg': 'BookingMemoLRs not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)



class GenerateBookingMemoPDF(APIView):
    def get(self, request, memo_no):
        # Fetch the booking memo details based on memo_no
        booking_memo = get_object_or_404(BookingMemo, memo_no=memo_no)

        # Optionally fetch company details if needed for the invoice
        company = get_object_or_404(CompanyMaster, flag=True, is_active=True)
        booking_lrs = booking_memo.lr_list.all()

        # Generate barcode for the memo_no  
        barcode_base64 = generate_barcode(memo_no)

        # Get the logged-in user's name
        user_profile = UserProfile.objects.get(user=booking_memo.created_by)
        user_name = user_profile.first_name + " "+user_profile.last_name

        # Render HTML to string using your booking memo data
        html_string = render( request,'booking_memo/booking_memo_pdf.html', {
            'company': company,
            'booking_memo': booking_memo,
            'lrs': booking_lrs,
            'barcode_base64': barcode_base64,  # Pass the barcode to the template
            'user_name': user_name,  # Pass the user's name to the template
        }).content.decode('utf-8')

        # Define CSS for styling (page size: Legal)
        css = CSS(string=''' 
            @page {
                size: legal;
                margin: 5mm;
            }
        ''')

        # Convert the HTML into a PDF document using WeasyPrint
        html = HTML(string=html_string)
        pdf = html.write_pdf(stylesheets=[css])

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=booking_memo_{memo_no}.pdf'

        user_profile = request.user.userprofile
        # Check if the user is a branch manager and if already printed
        if user_profile.role == 'branch_manager':
            if booking_memo.printed_by_branch_manager:
                return Response({"msg": "Invoice has already been printed by a branch manager.",'status': 'error'}, status=400)
            booking_memo.printed_by_branch_manager = True
            booking_memo.save()

        return response

class GenerateMemoNumberView(APIView):
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
            last_booking_memo = BookingMemo.objects.filter(
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

class CreateBookingMemoViews(APIView):
    def post(self, request, *args, **kwargs):     
        lr_list_data = request.data.get('lr_list', [])
        
        branch_id = request.data.get("branch_name")
        from_branch_id = request.data.get("from_branch")
        if branch_id != from_branch_id:
                return Response({
                    "status": "error",
                    "msg": "Login Branch and From Branch must be the same."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if lr_list_data is present
        if not lr_list_data:
            return Response({
                "message": "LR list data is required.",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)

        trip_no = request.data.get('trip_no')  
        if not trip_no:
            return Response({
                "status": "error",
                "msg": "Trip number (trip_no) is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate trip_no
        if trip_no in ['0', 0, None, ''] or not re.match(r'^\d{10}$', str(trip_no)):
            trip_no = 0
            
        # Retrieve TripMemo based on trip_no
        try:
            if trip_no != 0 :
                trip_memo = TripMemo.objects.filter(
                    trip_no=trip_no,
                    is_active=True,
                    flag=True
                ).order_by('-id').first()

                if not trip_memo:
                    return Response({
                        "status": "error",
                        "msg": "TripMemo not found for the given trip_no."
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validate that the trip is OPEN
                if trip_memo.trip_mode != 'OPEN':
                    return Response({
                        "status": "error",
                        "msg": "This Trip is not open."
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Validate that the vehicle_no matches
                vehicle_no = request.data.get('vehical_no')
                if trip_memo.vehicle_no_id != vehicle_no:
                    return Response({
                        "status": "error",
                        "msg": "This Booking Memo vehicle does not match the trip vehicle."
                    }, status=status.HTTP_400_BAD_REQUEST)

        except TripMemo.DoesNotExist:
            return Response({
                "status": "error",
                "msg": "TripMemo with the given trip_no not found."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Use the serializer with the request data
        bokking_memo_serializer = BookingMemoSerializer(data=request.data)
        
        if bokking_memo_serializer.is_valid():
            try:
                for item in lr_list_data:
                    # Validate each lr_list item
                    try:
                        lr_booking_instance = LR_Bokking.objects.get(pk=item['lr_booking']) if 'lr_booking' in item else None
                        if not lr_booking_instance:
                            return Response({
                                "message": f"LR Booking with id {item['lr_booking']} does not exist.",
                                "status": "error"
                            }, status=status.HTTP_400_BAD_REQUEST)

                        # Validate conditions for LR_Bokking
                        if lr_booking_instance.coll_type_id == 1:  # Assuming 1 corresponds to "LOCAL"
                            collection = Collection.objects.filter(
                                lr_booking=lr_booking_instance,
                                is_active=True,
                                flag=True
                            )
                            if not collection.exists():
                                return Response({
                                    "message": f"LR Booking with id {lr_booking_instance.lr_no} is LOCAL but collection is not completed.",
                                    "status": "error"
                                }, status=status.HTTP_400_BAD_REQUEST)
                            
                        # Additional validation for pay_type_id == 1
                        if lr_booking_instance.pay_type_id == 1:  # Assuming 1 corresponds to "PAID"
                            # Check in VoucherReceiptBranch
                            exists_in_voucher_receipt_branch = VoucherReceiptBranch.objects.filter(
                                lr_booking=lr_booking_instance,
                                is_active=True,
                                flag=True
                            ).exists()

                            # Check in MoneyReceipt
                            exists_in_money_receipt = MoneyReceipt.objects.filter(
                                lr_booking=lr_booking_instance,
                                is_active=True,
                                flag=True
                            ).exists()

                            # If not present in either model
                            if not (exists_in_voucher_receipt_branch or exists_in_money_receipt):
                                return Response({
                                    "message": f"LR Booking with id {lr_booking_instance.lr_no} has pay_type_id=1 (PAID) but is not linked with any active VoucherReceiptBranch or MoneyReceipt.",
                                    "status": "error"
                                }, status=status.HTTP_400_BAD_REQUEST)

                        # Validate related BookingMemoLRs
                        has_related_booking_memo = BookingMemoLRs.objects.filter(lr_booking=lr_booking_instance).exists()
                        if has_related_booking_memo:
                            related_booking_memos = BookingMemo.objects.filter(
                                lr_list__lr_booking=lr_booking_instance,
                                is_active=True,
                                flag=True
                            )
                            from_branch_id = request.data.get('from_branch')
                            if any(memo.from_branch_id == from_branch_id for memo in related_booking_memos):
                                return Response({
                                    "message": f"LR Booking with id {lr_booking_instance.lr_no} already has a BookingMemo linked with the same from_branch_id.",
                                    "status": "error"
                                }, status=status.HTTP_400_BAD_REQUEST)
                            
                            # Additional validation for the last BookingMemo
                            if related_booking_memos.exists():
                                last_booking_memo = related_booking_memos.last()

                                # Check if the last BookingMemo has a completed TripMemo
                                trip_memos = TripMemo.objects.filter(
                                    booking_memos__booking_memo=last_booking_memo,
                                    is_active=True,
                                    flag=True
                                )
                                if not trip_memos.exists():
                                    return Response({
                                        "message": f"For this LR {lr_booking_instance.lr_no}, the last BookingMemo {last_booking_memo.memo_no} TripMemo is not completed.",
                                        "status": "error"
                                    }, status=status.HTTP_400_BAD_REQUEST)

                                # Check if the last BookingMemo has a completed TruckUnloadingReport
                                tur = TruckUnloadingReport.objects.filter(
                                    memo_no=last_booking_memo,
                                    is_active=True,
                                    flag=True
                                ).first()
                                if not tur:
                                    return Response({
                                        "message": f"For this LR {lr_booking_instance.lr_no}, the last BookingMemo {last_booking_memo.memo_no} TUR is not completed.",
                                        "status": "error"
                                    }, status=status.HTTP_400_BAD_REQUEST)

                                # Check if the unloading branch matches the request from_branch
                                if tur.branch_name_id != from_branch_id:
                                    return Response({
                                        "message": f"For this LR {lr_booking_instance.lr_no}, the last BookingMemo {last_booking_memo.memo_no} TUR {tur.tur_no}'s unloading branch does not match with your request from_branch.",
                                        "status": "error"
                                    }, status=status.HTTP_400_BAD_REQUEST)

                    except LR_Bokking.DoesNotExist:
                        return Response({
                            "message": f"LR Booking with id {item['lr_booking']} does not exist.",
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)
                    except Exception as e:
                        return Response({
                            "message": f"An error occurred while validating LR Booking with id {item.get('lr_booking', 'Unknown')}.",
                            "status": "error",
                            "error": str(e)
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
                # Wrap everything in a transaction
                with transaction.atomic():                    
                    # Save the serializer, which also saves the BookingMemo instance
                    bokking_memo_instance = bokking_memo_serializer.save()  # This will save and return the instance
                    
                    lr_list_data_to_add = []
                    for item in lr_list_data:
                        # Check if lr_booking is valid and retrieve it if exists
                        lr_booking_instance = LR_Bokking.objects.get(pk=item['lr_booking']) if 'lr_booking' in item else None
                        coll_point_instance = CollectionTypes.objects.get(pk=item['coll_point']) if 'coll_point' in item else None
                        del_point_instance = DeliveryTypes.objects.get(pk=item['del_point']) if 'del_point' in item else None
                        
                        # Check if LR_Bokking instance is valid
                        if not lr_booking_instance:
                            return Response({
                                "message": f"LR Booking with id {item['lr_booking']} does not exist.",
                                "status": "error"
                            }, status=status.HTTP_400_BAD_REQUEST)

                        # Check if the lr_list item has an ID
                        if item.get('id') == 0:  # Create a new BookingMemoLRs instance
                            new_booking_memo_lr = BookingMemoLRs.objects.create(
                                lr_booking=lr_booking_instance,
                                coll_point=coll_point_instance,
                                del_point=del_point_instance,
                                lr_remarks=item.get('lr_remarks'),
                                created_by=request.user
                            )
                            lr_list_data_to_add.append(new_booking_memo_lr)
                        else:
                            # If the item has a valid ID, retrieve the existing BookingMemoLRs instance
                            existing_booking_memo_lr = BookingMemoLRs.objects.get(pk=item['id'])
                            existing_booking_memo_lr.lr_booking = lr_booking_instance
                            existing_booking_memo_lr.coll_point = coll_point_instance
                            existing_booking_memo_lr.del_point = del_point_instance
                            existing_booking_memo_lr.lr_remarks = item.get('lr_remarks')
                            existing_booking_memo_lr.save()
                            lr_list_data_to_add.append(existing_booking_memo_lr)

                    # Now set the lr_list after the BookingMemo instance has been saved
                    bokking_memo_instance.lr_list.set(lr_list_data_to_add)
                    
                    response_serializer = BookingMemoSerializer(bokking_memo_instance)

                    if trip_no != 0:
                        trip_bokking_memo_instance = TripBokkingMemos.objects.create(
                            booking_memo=bokking_memo_instance
                        )
                        trip_memo.booking_memos.add(trip_bokking_memo_instance)
                        trip_memo.save()

                    return Response({
                        "message": "Booking Memo created successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "message": "Validation failed",
            "status": "error",
            "errors": bokking_memo_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
class BookingMemoRetrieveView(APIView):

    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        effect_type_id = request.data.get('id')
        
        if not effect_type_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the BookingMemo instance
            instance = BookingMemo.objects.get(pk=effect_type_id)
            serializer = BookingMemoSerializer(instance)
            
            response_data = {
                'msg': 'BookingMemo type retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except BookingMemo.DoesNotExist:
            return Response({
                'msg': 'BookingMemo type not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class BookingMemoRetrieveAllView(APIView):
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


            # Retrieve all instances of BookingMemo
            instances = BookingMemo.objects.filter(
                flag=True
            ).filter(
                Q(branch_name__in=allowed_branches) | Q(from_branch__in=allowed_branches)  
            ).filter(
                Q(branch_name_id=branch_id) | Q(from_branch_id=branch_id)
            ).order_by('-id')

            serializer = BookingMemoSerializer(instances, many=True)
            
            response_data = {
                'msg': 'BookingMemo types retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving BookingMemo.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BookingMemoRetrieveFilteredView(APIView):   

    def post(self, request, *args, **kwargs):
        try:
            # Extract filter value for is_active from request data
            is_active = request.data.get('is_active', True)  # Default to True if not provided
            
            # Filter instances based on is_active value
            queryset = BookingMemo.objects.filter(is_active=is_active,flag=True).order_by('-id')
            serializer = BookingMemoSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'BookingMemo retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving BookingMemo.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BookingMemoFilterView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(BookingMemo, filters)

            # Serialize the filtered data
            serializer = BookingMemoSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

# class BookingMemoRetrieveTripMemoView(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             # Extracting the required parameters from the request body
#             from_branch_id = request.data.get('from_branch_id')

#             # Ensure from_branch_id is provided
#             if not from_branch_id:
#                 return Response({
#                     'status': 'error',
#                     'message': 'from_branch id is required.'
#                 }, status=status.HTTP_400_BAD_REQUEST)

#             # Filtering the BookingMemo queryset based on the provided parameters
#             queryset = BookingMemo.objects.filter(is_active=True, flag=True)

#             filtered_queryset = []
#             for memo_booking in queryset:
#                 # Check if there are any TripBokkingMemos related to this BookingMemo
#                 has_related_trip_memo = TripBokkingMemos.objects.filter(booking_memo=memo_booking).exists()

#                 if has_related_trip_memo:
#                     # If there are related TripBokkingMemos, check their associated BookingMemo's from_branch
#                     related_booking_memos = TripMemo.objects.filter(booking_memos__booking_memo=memo_booking)

#                     # Exclude the memo_booking if any BookingMemo has the same from_branch
#                     if any(memo.from_branch_id == from_branch_id for memo in related_booking_memos):
#                         continue  # Exclude this memo_booking

#                     # If no exclusion criteria are met, keep this BookingMemo in the final list
#                     filtered_queryset.append(memo_booking)

#             # Prepare the response data with only the required fields
#             response_data = [
#                 {
#                     'id': memo_booking.id,
#                     'memo_no': memo_booking.memo_no
#                 }
#                 for memo_booking in filtered_queryset
#             ]

#             # Return success response with serialized data
#             return Response({
#                 'msg': 'Booking Memo retrieved successfully',
#                 'status': 'success',
#                 'data': [response_data]
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             # Handle unexpected exceptions
#             return Response({
#                 'status': 'error',
#                 'message': 'An unexpected error occurred',
#                 'error': str(e)  # Include the error message for debugging
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BookingMemoRetrieveTripMemoView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extracting the required parameter from the request body
            from_branch_id = request.data.get('from_branch_id')

            # Ensure from_branch_id is provided
            if not from_branch_id:
                return Response({
                    'status': 'error',
                    'message': 'from_branch id is required.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Filtering BookingMemo instances based on provided parameters and excluding those linked to TripBokkingMemos
            queryset = BookingMemo.objects.filter(is_active=True, flag=True).exclude(
                id__in=TripBokkingMemos.objects.values_list('booking_memo_id', flat=True)
            )

            # Further filter the queryset by from_branch_id if needed
            filtered_queryset = [
                memo_booking for memo_booking in queryset if memo_booking.from_branch_id == from_branch_id
            ]

            # Prepare the response data with only the required fields
            # response_data = [
            #     {
            #         'id': memo_booking.id,
            #         'memo_no': memo_booking.memo_no
            #     }
            #     for memo_booking in filtered_queryset
            # ]

            new_response_data=BookingMemoSerializer(filtered_queryset,many=True)        
            # Return success response with serialized data
            return Response({
                'msg': 'Booking Memo retrieved successfully',
                'status': 'success',
                # 'data': response_data
                'data': new_response_data.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BookingMemoRetrieveTURView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extracting the required parameter from the request body
            to_branch_id = request.data.get('to_branch_id')

            # Ensure from_branch_id is provided
            if not to_branch_id:
                return Response({
                    'status': 'error',
                    'message': 'to_branch id is required.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Filtering BookingMemo instances based on provided parameters and excluding those linked to TripBokkingMemos
            queryset = BookingMemo.objects.filter(is_active=True, flag=True).exclude(
                id__in=TruckUnloadingReport.objects.values_list('memo_no_id', flat=True)
            )

            valid_booking_memos = []
            for memo in queryset:
                # Check if the memo is linked to any incomplete TripMemo
                linked_trip_memos = TripMemo.objects.filter(
                    booking_memos__booking_memo=memo
                )
                # If any linked TripMemo is inactive or flagged, exclude it
                if not linked_trip_memos.filter(is_active=True, flag=True).exists():
                    continue  # Skip this memo if any linked TripMemo is incomplete
                valid_booking_memos.append(memo)

            # Further filter the queryset by from_branch_id if needed
            filtered_queryset = [
                memo_booking for memo_booking in queryset if memo_booking.to_branch_id == to_branch_id
            ]

            # Prepare the response data with only the required fields
            # response_data = [
            #     {
            #         'id': memo_booking.id,
            #         'memo_no': memo_booking.memo_no
            #     }
            #     for memo_booking in filtered_queryset
            # ]

            new_response_data=BookingMemoSerializer(filtered_queryset,many=True)        
            # Return success response with serialized data
            return Response({
                'msg': 'Booking Memo retrieved successfully',
                'status': 'success',
                # 'data': response_data
                'data': new_response_data.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BookingMemoLrslistRetrieveView(APIView):
    
    def post(self, request, *args, **kwargs):
        # Extract ID or memo_no from request data
        effect_type_id = request.data.get('id')
        memo_no = request.data.get('memo_no')
        
        # If neither 'id' nor 'memo_no' is provided, return an error
        if not effect_type_id and not memo_no:
            return Response({
                'msg': 'Either ID or memo_no is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if effect_type_id:
                # Retrieve the BookingMemo instance by id
                instance = BookingMemo.objects.get(pk=effect_type_id)
            elif memo_no:
                # Retrieve the BookingMemo instance by memo_no
                instance = BookingMemo.objects.get(memo_no=memo_no)
            
            # Serialize the related LR_Bokking entries from the BookingMemo's lr_list
            lr_bookings = instance.lr_list.values('lr_booking')  # Retrieve only lr_booking IDs

            # Get the related LR_Bokking details
            lr_booking_details = LR_Bokking.objects.filter(lr_no__in=[lr['lr_booking'] for lr in lr_bookings])

            # If no related LR_Bokking objects are found
            if not lr_booking_details.exists():
                return Response({
                    'msg': 'No related LR_Bokking found',
                    'status': 'error',
                    'data': {}
                }, status=status.HTTP_404_NOT_FOUND)

            booking_memo_serializer = BookingMemoSerializer(instance)
            # Serialize the LR_Bokking objects to return all their fields
            serializer = LRBokkingSerializer(lr_booking_details, many=True)

            # Prepare response data
            response_data = {
                'msg': 'BookingMemo related LR_Bokking retrieved successfully',
                'status': 'success',
                'data': [{                
                        'memo': booking_memo_serializer.data,                
                        'lr_bookings': serializer.data
                }]
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except BookingMemo.DoesNotExist:
            return Response({
                'msg': 'BookingMemo not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class BookingMemoUpdateAPIView(APIView):    
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        booking_memo_id = request.data.get('id')

        branch_id = request.data.get("branch_name")
        from_branch_id = request.data.get("from_branch")
        if branch_id != from_branch_id:
                return Response({
                    "status": "error",
                    "msg": "Login Branch and From Branch must be the same."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if not booking_memo_id:
            return Response({
                'msg': 'Booking Memo ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the BookingMemo instance
            booking_memo_instance = BookingMemo.objects.get(pk=booking_memo_id)
            
            # Initialize serializer with the instance and updated data
            serializer = BookingMemoSerializer(booking_memo_instance, data=request.data, partial=True)
            
            if serializer.is_valid():

                # Get the 'lr_list' from the request
                lr_list_data = request.data.get('lr_list', [])
                # Validating LR list
                if lr_list_data:
                    for item in lr_list_data:
                        try:
                            lr_booking_instance = LR_Bokking.objects.get(pk=item['lr_booking']) if 'lr_booking' in item else None
                            if not lr_booking_instance:
                                return Response({
                                    "message": f"LR Booking with id {item['lr_booking']} does not exist.",
                                    "status": "error"
                                }, status=status.HTTP_400_BAD_REQUEST)

                            # Validate conditions for LR_Bokking
                            if lr_booking_instance.coll_type_id == 1:  # Assuming 1 corresponds to "LOCAL"
                                collection = Collection.objects.filter(
                                    lr_booking=lr_booking_instance,
                                    is_active=True,
                                    flag=True
                                )
                                if not collection.exists():
                                    return Response({
                                        "message": f"LR Booking with id {lr_booking_instance.lr_no} is LOCAL but collection is not completed.",
                                        "status": "error"
                                    }, status=status.HTTP_400_BAD_REQUEST)

                            if lr_booking_instance.pay_type_id == 1:  # Assuming 1 corresponds to "PAID"
                                exists_in_voucher_receipt_branch = VoucherReceiptBranch.objects.filter(
                                    lr_booking=lr_booking_instance,
                                    is_active=True,
                                    flag=True
                                ).exists()
                                exists_in_money_receipt = MoneyReceipt.objects.filter(
                                    lr_booking=lr_booking_instance,
                                    is_active=True,
                                    flag=True
                                ).exists()
                                if not (exists_in_voucher_receipt_branch or exists_in_money_receipt):
                                    return Response({
                                        "message": f"LR Booking with id {lr_booking_instance.lr_no} has pay_type_id=1 (PAID) but is not linked with any active VoucherReceiptBranch or MoneyReceipt.",
                                        "status": "error"
                                    }, status=status.HTTP_400_BAD_REQUEST)

                            has_related_booking_memo = BookingMemoLRs.objects.filter(lr_booking=lr_booking_instance).exists()
                            if has_related_booking_memo:
                                # Exclude the current BookingMemo instance from the query
                                related_booking_memos = BookingMemo.objects.filter(
                                    lr_list__lr_booking=lr_booking_instance,
                                    is_active=True,
                                    flag=True
                                ).exclude(pk=booking_memo_instance.pk)  # Exclude the current instance

                                from_branch_id = request.data.get('from_branch')
                                if any(memo.from_branch_id == from_branch_id for memo in related_booking_memos):
                                    return Response({
                                        "message": f"LR Booking with id {lr_booking_instance.lr_no} already has a BookingMemo linked with the same from_branch_id.",
                                        "status": "error"
                                    }, status=status.HTTP_400_BAD_REQUEST)
                                
                                # # Additional validation for the last BookingMemo
                                # if related_booking_memos.exists():
                                #     last_booking_memo = related_booking_memos.last()

                                #     # Check if the last BookingMemo has a completed TripMemo
                                #     trip_memos = TripMemo.objects.filter(
                                #         booking_memos__booking_memo=last_booking_memo,
                                #         is_active=True,
                                #         flag=True
                                #     )
                                #     if not trip_memos.exists():
                                #         return Response({
                                #             "message": f"For this LR {lr_booking_instance.lr_number}, the next BookingMemo's {last_booking_memo.memo_no}, TripMemo is not completed.",
                                #             "status": "error"
                                #         }, status=status.HTTP_400_BAD_REQUEST)

                                #     # Check if the last BookingMemo has a completed TruckUnloadingReport
                                #     tur = TruckUnloadingReport.objects.filter(
                                #         memo_no=last_booking_memo,
                                #         is_active=True,
                                #         flag=True
                                #     ).first()
                                #     if not tur:
                                #         return Response({
                                #             "message": f"For this LR {lr_booking_instance.lr_number}, the last BookingMemo's {last_booking_memo.memo_no}, TUR is not completed.",
                                #             "status": "error"
                                #         }, status=status.HTTP_400_BAD_REQUEST)

                                #     # Check if the unloading branch matches the request from_branch
                                #     if tur.branch_name_id != from_branch_id:
                                #         return Response({
                                #             "message": f"For this LR {lr_booking_instance.lr_number}, the last BookingMemo's {last_booking_memo.memo_no} TUR {tur.tur_no}'s unloading branch does not match with your request from_branch.",
                                #             "status": "error"
                                #         }, status=status.HTTP_400_BAD_REQUEST)

                        except LR_Bokking.DoesNotExist:
                            return Response({
                                "message": f"LR Booking with id {item['lr_booking']} does not exist.",
                                "status": "error"
                            }, status=status.HTTP_400_BAD_REQUEST)

                # Save the updated instance
                serializer.save(updated_by=request.user)                                

                # Handle lr_list updates
                if lr_list_data is not None:
                    # Fetch existing lr_list linked to the instance
                    existing_lr_list = list(booking_memo_instance.lr_list.all())
                    
                    # If the list is empty, delete all existing lr_list items
                    if not lr_list_data:  # If no new lr_list items are provided
                        for lr in existing_lr_list:
                            lr.delete()
                        booking_memo_instance.lr_list.clear()  # Clear the relation
                    else:
                        # Create a map of existing LR_Memo IDs for quick lookup
                        existing_lr_ids = {lr.id for lr in existing_lr_list}
                        
                        # Extract new LR IDs from the request
                        new_lr_ids = {item.get('id') for item in lr_list_data if item.get('id') != 0}
                        
                        # Identify LR items to delete
                        lr_to_delete = [lr for lr in existing_lr_list if lr.id not in new_lr_ids]
                        
                        # Delete lr_list items that are no longer linked
                        for lr in lr_to_delete:
                            lr.delete()

                        # Initialize lists to keep track of new and updated lr_list items
                        lr_to_add = []
                        lr_to_update = []

                        for item in lr_list_data:
                            # Check if the item has an ID
                            if item.get('id') == 0:  # New record
                                lr_booking_instance = LR_Bokking.objects.get(pk=item['lr_booking']) if 'lr_booking' in item else None
                                coll_point_instance = CollectionTypes.objects.get(pk=item['coll_point']) if 'coll_point' in item else None
                                del_point_instance = DeliveryTypes.objects.get(pk=item['del_point']) if 'del_point' in item else None

                                # Create a new BookingMemoLRs instance
                                new_lr_memo = BookingMemoLRs.objects.create(
                                    lr_booking=lr_booking_instance,
                                    coll_point=coll_point_instance,
                                    del_point=del_point_instance,
                                    lr_remarks=item.get('lr_remarks'),
                                    created_by=request.user
                                )
                                lr_to_add.append(new_lr_memo)
                            else:  # Existing record
                                existing_lr_memo = BookingMemoLRs.objects.get(pk=item['id'])
                                existing_lr_memo.lr_booking = LR_Bokking.objects.get(pk=item['lr_booking']) if 'lr_booking' in item else None
                                existing_lr_memo.coll_point = CollectionTypes.objects.get(pk=item['coll_point']) if 'coll_point' in item else None
                                existing_lr_memo.del_point = DeliveryTypes.objects.get(pk=item['del_point']) if 'del_point' in item else None
                                existing_lr_memo.lr_remarks = item.get('lr_remarks')
                                existing_lr_memo.save()
                                lr_to_update.append(existing_lr_memo)

                        # Now set the lr_list after the BookingMemo instance has been saved
                        booking_memo_instance.lr_list.set(lr_to_add + lr_to_update)

                return Response({
                    'msg': 'Booking Memo updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)

            return Response({
                'msg': 'Failed to update Booking Memo',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except BookingMemo.DoesNotExist:
            return Response({
                'msg': 'Booking Memo not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except CollectionTypes.DoesNotExist:
            return Response({"error": "CollectionTypes not found"}, status=status.HTTP_400_BAD_REQUEST)
        except DeliveryTypes.DoesNotExist:
            return Response({"error": "DeliveryTypes not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'msg': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class BookingMemoUpdateAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         # Extract ID from request data
#         booking_memo_id = request.data.get('id')

#         if not booking_memo_id:
#             return Response({
#                 'msg': 'Booking Memo ID is required',
#                 'status': 'error',
#                 'data': {}
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # Retrieve the BookingMemo instance
#             booking_memo_instance = BookingMemo.objects.get(pk=booking_memo_id)
            
#             # Initialize serializer with the instance and updated data
#             serializer = BookingMemoSerializer(booking_memo_instance, data=request.data, partial=True)
            
#             if serializer.is_valid():
#                 # Save the updated instance
#                 serializer.save(updated_by=request.user)
                
#                 # Get the 'lr_list' from the request
#                 lr_list_data = request.data.get('lr_list', [])

#                 if lr_list_data:
#                     try:
#                         # Fetch existing lr_list linked to the instance
#                         existing_lr_list = list(booking_memo_instance.lr_list.all())
                        
#                         # Create a map of existing LR_Memo IDs for quick lookup
#                         existing_lr_ids = {lr.id for lr in existing_lr_list}
                        
#                         # Extract new LR IDs from the request
#                         new_lr_ids = {item.get('id') for item in lr_list_data if item.get('id') != 0}
                        
#                         # Identify LR items to delete
#                         lr_to_delete = [lr for lr in existing_lr_list if lr.id not in new_lr_ids]
                        
#                         # Delete lr_list items that are no longer linked
#                         for lr in lr_to_delete:
#                             lr.delete()

#                         # Initialize lists to keep track of new and updated lr_list items
#                         lr_to_add = []
#                         lr_to_update = []

#                         for item in lr_list_data:
#                             # Check if the item has an ID
#                             if item.get('id') == 0:  # New record
#                                 lr_booking_instance = LR_Bokking.objects.get(pk=item['lr_booking']) if 'lr_booking' in item else None
#                                 coll_point_instance = CollectionTypes.objects.get(pk=item['coll_point']) if 'coll_point' in item else None
#                                 del_point_instance = DeliveryTypes.objects.get(pk=item['del_point']) if 'del_point' in item else None

#                                 # Create a new BookingMemoLRs instance
#                                 new_lr_memo = BookingMemoLRs.objects.create(
#                                     lr_booking=lr_booking_instance,
#                                     coll_point=coll_point_instance,
#                                     del_point=del_point_instance,
#                                     lr_remarks=item.get('lr_remarks'),
#                                     created_by=request.user
#                                 )
#                                 lr_to_add.append(new_lr_memo)
#                             else:  # Existing record
#                                 existing_lr_memo = BookingMemoLRs.objects.get(pk=item['id'])
#                                 existing_lr_memo.lr_booking = LR_Bokking.objects.get(pk=item['lr_booking']) if 'lr_booking' in item else None
#                                 existing_lr_memo.coll_point = CollectionTypes.objects.get(pk=item['coll_point']) if 'coll_point' in item else None
#                                 existing_lr_memo.del_point = DeliveryTypes.objects.get(pk=item['del_point']) if 'del_point' in item else None
#                                 existing_lr_memo.lr_remarks = item.get('lr_remarks')
#                                 existing_lr_memo.save()
#                                 lr_to_update.append(existing_lr_memo)

#                         # Now set the lr_list after the BookingMemo instance has been saved
#                         booking_memo_instance.lr_list.set(lr_to_add + lr_to_update)
                    
#                     except ItemDetailsMaster.DoesNotExist:
#                         return Response({"error": "ItemDetailsMaster not found"}, status=status.HTTP_400_BAD_REQUEST)
#                     except CollectionTypes.DoesNotExist:
#                         return Response({"error": "CollectionTypes not found"}, status=status.HTTP_400_BAD_REQUEST)
#                     except DeliveryTypes.DoesNotExist:
#                         return Response({"error": "DeliveryTypes not found"}, status=status.HTTP_400_BAD_REQUEST)

#                 return Response({
#                     'msg': 'Booking Memo updated successfully',
#                     'status': 'success',
#                     'data': [serializer.data]
#                 }, status=status.HTTP_200_OK)
            
#             return Response({
#                 'msg': 'Failed to update Booking Memo',
#                 'status': 'error',
#                 'errors': serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         except BookingMemo.DoesNotExist:
#             return Response({
#                 'msg': 'Booking Memo not found',
#                 'status': 'error',
#                 'data': {}
#             }, status=status.HTTP_404_NOT_FOUND)

class BookingMemoSoftDeleteAPIView(APIView):
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
            # Retrieve the BookingMemo instance
            instance = BookingMemo.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'BookingMemo deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except BookingMemoLRs.DoesNotExist:
            return Response({
                'msg': 'BookingMemo not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class BookingMemoPermanentDeleteAPIView(APIView):
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
            # Retrieve the BookingMemo instance
            instance = BookingMemo.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'BookingMemo permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except BookingMemo.DoesNotExist:
            return Response({
                'msg': 'BookingMemo not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)



class TripModeCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the request data and context
            serializer = TripModeSerializer(data=request.data, context={'request': request})

            # Validate the incoming data
            if serializer.is_valid():
                # Save the serializer, which triggers the save method in the model
                serializer.save(created_by=request.user)

                # Return a success response with data and a custom message
                return Response({
                    "status": "success",
                    "message": "Trip Mode created successfully.",
                    "data": [serializer.data]
                }, status=status.HTTP_201_CREATED)

            # If the data is not valid, return an error response
            return Response({
                "status": "error",
                "message": "There was an error creating the trip mode.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while creating the trip mode.",
                "error": str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TripModeRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract 'id' from request data to identify the record to retrieve
        trip_mode_id = request.data.get('id')

        if trip_mode_id is None:
            return Response({
                "status": "error",
                "message": "No ID provided.",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the trip mode from the database
            trip_mode = TripMode.objects.get(pk=trip_mode_id)
        except TripMode.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Trip mode not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item data
        serializer = TripModeSerializer(trip_mode)

        # Return a success response with the item data
        return Response({
            "status": "success",
            "message": "Trip mode retrieved successfully.",
            "data": [serializer.data]
        }, status=status.HTTP_200_OK)

class TripModeRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = TripMode.objects.filter(flag=True).order_by('-id')

            # Serialize the items data
            serializer = TripModeSerializer(items, many=True)

            # Return a success response with the items data
            return Response({
                "status": "success",
                "message": "Trip modes retrieved successfully.",
                "data": [serializer.data]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while retrieving the trip modes.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TripModeRetrieveActiveView (APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = TripMode.objects.filter(is_active=True,flag=True).order_by('-id')

            # Serialize the items data
            serializer = TripModeSerializer(items, many=True)

            # Return a success response with the items data
            return Response({
                "status": "success",
                "message": "Trip modes retrieved successfully.",
                "data": [serializer.data]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while retrieving the trip modes.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TripModeUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        trip_mode_id = request.data.get('id')

        if not trip_mode_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the TripMode instance
            instance = TripMode.objects.get(pk=trip_mode_id)

            # Initialize serializer with the instance and updated data
            serializer = TripModeSerializer(instance, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'Trip mode updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)

            return Response({
                'msg': 'Failed to update Trip mode',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except TripMode.DoesNotExist:
            return Response({
                'msg': 'Trip mode not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TripModeSoftDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        trip_mode_id = request.data.get('id')

        if not trip_mode_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the TripMode instance
            instance = TripMode.objects.get(pk=trip_mode_id)

            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()

            return Response({
                'msg': 'Trip mode deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)

        except TripMode.DoesNotExist:
            return Response({
                'msg': 'Trip mode not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class TripModePermanentDeleteAPIView(APIView):

    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        trip_mode_id = request.data.get('id')

        if not trip_mode_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the TripMode instance
            instance = TripMode.objects.get(pk=trip_mode_id)

            # Permanently delete the instance
            instance.delete()

            return Response({
                'msg': 'Trip mode permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)

        except TripMode.DoesNotExist:
            return Response({
                'msg': 'Trip mode not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)



class VehicalHireContractCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the request data
            serializer = VehicalHireContractSerializer(data=request.data)
            
            # Validate the serializer
            if serializer.is_valid():
                # Save the instance with the user from the request
                serializer.save(created_by=request.user)
                
                # Return a success response with the serialized data
                return Response({
                    'message': 'Vehical Hire Contract created successfully!',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'message': 'Error creating Vehical Hire Contract',
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

class VehicalHireContractRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'id' in the POST data
        contract_id = request.data.get('id')

        # Check if 'id' is provided
        if not contract_id:
            return Response({
                'message': 'Vehical Hire Contract ID is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the VehicalHireContract instance
            contract = VehicalHireContract.objects.get(id=contract_id)
        except VehicalHireContract.DoesNotExist:
            return Response({
                'message': 'Vehical Hire Contract not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = VehicalHireContractSerializer(contract)

        # Return the data with success status
        return Response({
            'message': 'Vehical Hire Contract retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)
    
class VehicalHireContractRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = VehicalHireContract.objects.filter(flag=True).order_by('-id')

            # Serialize the items data
            serializer = VehicalHireContractSerializer(items, many=True)

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
    
class VehicalHireContractRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter the queryset for active VehicalHireContract instances
            queryset = VehicalHireContract.objects.filter(is_active=True, flag=True).order_by('-id')
            serializer = VehicalHireContractSerializer(queryset, many=True)

            # Prepare the response data
            response_data = {
                'msg': 'Vehical Hire Contracts retrieved successfully',
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
    
class VehicalHireContractUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        contract_id = request.data.get('id')
        
        if not contract_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the VehicalHireContract instance
            instance = VehicalHireContract.objects.get(pk=contract_id)
            
            # Initialize serializer with the instance and updated data
            serializer = VehicalHireContractSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'Vehical Hire Contract updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update Vehical Hire Contract',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except VehicalHireContract.DoesNotExist:
            return Response({
                'msg': 'Vehical Hire Contract not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VehicalHireContractSoftDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        contract_id = request.data.get('id')
        
        if not contract_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the VehicalHireContract instance
            instance = VehicalHireContract.objects.get(pk=contract_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'Vehical Hire Contract deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except VehicalHireContract.DoesNotExist:
            return Response({
                'msg': 'Vehical Hire Contract not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class VehicalHireContractPermanentDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        contract_id = request.data.get('id')
        
        if not contract_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the VehicalHireContract instance
            instance = VehicalHireContract.objects.get(pk=contract_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'Vehical Hire Contract permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except VehicalHireContract.DoesNotExist:
            return Response({
                'msg': 'Vehical Hire Contract not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class GetVehicleHireContracts(APIView):
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
            # Fetch the first active VehicleHireContract instance based on branch IDs
            vehicle_hire_contract = VehicalHireContract.objects.filter(
                from_branch_id=from_branch_id,
                to_branch_id=to_branch_id,
                is_active=True
            )

            if not vehicle_hire_contract:
                return Response({
                    'message': 'No active Vehicle Hire Contract found for the provided branches',
                    'status': 'error',
                    'data': []
                }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'message': 'Error fetching Vehicle Hire Contract',
                'status': 'error',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Serialize the retrieved instance
        serializer = VehicalHireContractSerializer(vehicle_hire_contract,many=True)

        # Return the data with success status
        return Response({
            'message': 'Vehicle Hire Contract retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)

class GetVehicleHireContractByvehicalType(APIView):
    def post(self, request, *args, **kwargs):
        # Expecting 'from_branch_id' and 'to_branch_id' in the POST data
        from_branch_id = request.data.get('from_branch_id')
        to_branch_id = request.data.get('to_branch_id')
        vehical_type_id = request.data.get('vehical_type_id')  # Assuming this is relevant for your use case

        # Check if 'from_branch_id' and 'to_branch_id' are provided
        if not from_branch_id or not to_branch_id:
            return Response({
                'message': 'Both from_branch_id and to_branch_id are required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            # Fetch the first active VehicleHireContract instance based on branch IDs
            vehicle_hire_contract = VehicalHireContract.objects.filter(
                from_branch_id=from_branch_id,
                to_branch_id=to_branch_id,
                vehical_type_id=vehical_type_id,
                is_active=True,
                flag=True
            ).first()

            if not vehicle_hire_contract:
                return Response({
                    'message': 'No active Vehicle Hire Contract found for the provided branches',
                    'status': 'error',
                    'data': []
                }, status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            return Response({
                'message': 'Error fetching Vehicle Hire Contract',
                'status': 'error',
                'data': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Serialize the retrieved instance
        serializer = VehicalHireContractSerializer(vehicle_hire_contract)

        # Return the data with success status
        return Response({
            'message': 'Vehicle Hire Contract retrieved successfully',
            'status': 'success',
            'data': [serializer.data]
        }, status=status.HTTP_200_OK)



class GenerateTripMemoPDF(APIView):
    def get(self, request, trip_no):
        # Fetch the TripMemo details based on trip_no
        trip_memo = get_object_or_404(TripMemo, trip_no=trip_no)

        trip_booking_memos = trip_memo.booking_memos.all()

        # Optionally fetch company details if needed for the memo
        company = get_object_or_404(CompanyMaster, flag=True, is_active=True)

        # Generate barcode for the trip_no (Assuming you have a barcode generation function)
        barcode_base64 = generate_barcode(trip_no)

        # Get the logged-in user's name
        user_profile = UserProfile.objects.get(user=trip_memo.created_by)
        user_name = user_profile.first_name + " "+user_profile.last_name

        # Render HTML to string using your Trip Memo data
        html_string = render(request,'trip_memo/trip_memo_pdf.html', {
            'company': company,
            'trip_memo': trip_memo,
            'lrs': trip_booking_memos,
            'barcode_base64': barcode_base64,  # Pass the barcode to the template
            'user_name': user_name,  # Pass the user's name to the template
        }).content.decode('utf-8')

        # Define CSS for styling (page size: Legal)
        css = CSS(string=''' 
            @page {
                size: legal;
                margin: 5mm;
            }
        ''')

        # Convert the HTML into a PDF document using WeasyPrint
        html = HTML(string=html_string)
        pdf = html.write_pdf(stylesheets=[css])

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=trip_memo_{trip_no}.pdf'

        user_profile = request.user.userprofile
        # Check if the user is a branch manager and if already printed
        if user_profile.role == 'branch_manager':
            if trip_memo.printed_by_branch_manager:
                return Response({"msg": "Invoice has already been printed by a branch manager.",'status': 'error'}, status=400)
            trip_memo.printed_by_branch_manager = True
            trip_memo.save()

        return response

class GenerateTripNumberView(APIView):
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
            last_trip_memo = TripMemo.objects.filter(
                branch_id=branch_id,
                trip_no__startswith=prefix
            ).exclude(trip_no__isnull=True).exclude(trip_no__exact='').order_by('-trip_no').first()

            if last_trip_memo:
                last_sequence_number = int(last_trip_memo.trip_no[len(prefix):])
                new_memo_no = f"{prefix}{str(last_sequence_number + 1).zfill(5)}"
            else:
                new_memo_no = f"{prefix}00001"

            # On successful LR number generation
            response_data = {
                'msg': 'Trip number generated successfully',
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
                'message': 'An error occurred during Trip number generation due to invalid data.',
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

class TripMemoCreateView(APIView):        
    def post(self, request, *args, **kwargs):
        print(request.data)
        # Extracting trip booking memos data from the request
        booking_memos_data = request.data.get('booking_memos', [])    
        from_branch = request.data.get('from_branch')
        vehicle_no = request.data.get('vehicle_no')
        driver_name = request.data.get('driver_name')   

        branch_id = request.data.get("branch")
        from_branch_id = request.data.get("from_branch")
        if branch_id != from_branch_id:
                return Response({
                    "status": "error",
                    "msg": "Login Branch and From Branch must be the same."
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if booking memos data is present
        if not booking_memos_data:
            return Response({
                "message": "Booking memos data is required.",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)
        if not all([from_branch, vehicle_no, driver_name]):
            return Response({
                "message": "from_branch, vehicle_no, and driver_name are required fields.",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate booking memos
        invalid_memos = []
        for item in booking_memos_data:
            booking_memo_id = item.get('booking_memo')
            try:
                # Retrieve the BookingMemo instance
                booking_memo_instance = BookingMemo.objects.get(pk=booking_memo_id)
            except BookingMemo.DoesNotExist:
                invalid_memos.append({
                    "id": booking_memo_id,
                    "error": f"BookingMemo with id {booking_memo_id} does not exist."
                })
                continue

            # Check validations
            if booking_memo_instance.from_branch_id != from_branch:
                invalid_memos.append({
                    "id": booking_memo_id,
                    "error": "This booking memos's from_branch does not match the trip's from_branch."
                })
            if booking_memo_instance.vehical_no_id != vehicle_no:
                invalid_memos.append({
                    "id": booking_memo_id,
                    "error": "This booking memos's vehicle_no does not match the trip's vehicle_no."
                })
            # if booking_memo_instance.driver_name_id != driver_name:
            #     invalid_memos.append({
            #         "id": booking_memo_id,
            #         "error": "This booking memos's driver_name does not match the trip's driver_name."
            #     })

            # Validate related BookingMemoLRs
            has_related_trip_booking_memo = TripBokkingMemos.objects.filter(booking_memo=booking_memo_instance).first()

            if has_related_trip_booking_memo:
                # Check if the related TripMemo exists with the booking memo and is active and flagged
                related_trip_memo = TripMemo.objects.filter(
                    booking_memos=has_related_trip_booking_memo,
                    is_active=True,
                    flag=True
                ).exists()
                
                if related_trip_memo:
                    return Response({
                        "message": f"BookingMemo with ID {booking_memo_instance.id} is already associated with an active TripMemo.",
                        "status": "error"
                    }, status=status.HTTP_400_BAD_REQUEST)     
        
        if invalid_memos:
            return Response({
                "message": "Validation errors in booking memos.",
                "status": "error",
                "errors": invalid_memos
            }, status=status.HTTP_400_BAD_REQUEST)
        

        # Use the TripMemo serializer with the request data
        trip_memo_serializer = TripMemoSerializer(data=request.data)
        
        if trip_memo_serializer.is_valid():
            try:
                # Wrap everything in a transaction to ensure atomicity
                with transaction.atomic():
                    # Save the serializer, which saves the TripMemo instance
                    trip_memo_instance = trip_memo_serializer.save(created_by=request.user)
                    
                    booking_memos_to_add = []
                    for item in booking_memos_data:                
                        # Retrieve the related BookingMemo instance
                        booking_memo_instance = BookingMemo.objects.get(pk=item['booking_memo']) if 'booking_memo' in item else None                      
                        # Check if the booking memo instance is valid
                        if not booking_memo_instance:
                            return Response({
                                "message": f"Booking memo with id {item['booking_memo']} does not exist.",
                                "status": "error"
                            }, status=status.HTTP_400_BAD_REQUEST)
                        
                        if booking_memo_instance.trip_no == 0 or booking_memo_instance.trip_no == '0':
                            booking_memo_instance.trip_no = trip_memo_instance.trip_no
                            booking_memo_instance.save()


                        # Check if the booking memo list item has an ID (update scenario)
                        if item.get('id') == 0:  # Create a new TripBokkingMemos instance
                            new_booking_memo = TripBokkingMemos.objects.create(
                                booking_memo=booking_memo_instance,
                                remark=item.get('remark', ''),
                                created_by=request.user
                            )
                            booking_memos_to_add.append(new_booking_memo)
                        else:
                            # If the item has a valid ID, retrieve the existing TripBokkingMemos instance
                            existing_booking_memo = TripBokkingMemos.objects.get(pk=item['id'])
                            existing_booking_memo.booking_memo = booking_memo_instance
                            existing_booking_memo.remark = item.get('remark', '')
                            existing_booking_memo.save()
                            booking_memos_to_add.append(existing_booking_memo)

                    # Now set the booking memos after the TripMemo instance has been saved
                    trip_memo_instance.booking_memos.set(booking_memos_to_add)

                    # Update availability of Vehicle and Driver
                    if trip_memo_instance.vehicle_no:
                        trip_memo_instance.vehicle_no.is_available = False
                        trip_memo_instance.vehicle_no.save()

                    # if trip_memo_instance.driver_name:
                    #     trip_memo_instance.driver_name.is_available = False
                    #     trip_memo_instance.driver_name.save()

                    # Serialize the saved TripMemo instance
                    response_serializer = TripMemoSerializer(trip_memo_instance)
                    return Response({
                        "message": "Trip Memo created successfully!",
                        "status": "success",
                        "data": response_serializer.data
                    }, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "message": "Validation failed",
            "status": "error",
            "errors": trip_memo_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class TripMemoUpdateView(APIView):    
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        trip_memo_id = request.data.get('id')
        booking_memos_data = request.data.get('booking_memos', [])
        from_branch = request.data.get('from_branch')
        vehicle_no = request.data.get('vehicle_no')
        driver_name = request.data.get('driver_name')       
        if not trip_memo_id:
            return Response({
                'message': 'Trip Memo ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        if not booking_memos_data:
            return Response({
                "message": "Booking memos data is required.",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)
        if not all([from_branch, vehicle_no, driver_name]):
            return Response({
                "message": "from_branch, vehicle_no, and driver_name are required fields.",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        trip_memo_instance = get_object_or_404(TripMemo, pk=trip_memo_id)

        # Validate booking memos
        invalid_memos = []
        valid_booking_memo_ids = []
        for item in booking_memos_data:
            booking_memo_id = item.get('booking_memo')
            try:
                # Retrieve the BookingMemo instance
                booking_memo_instance = BookingMemo.objects.get(pk=booking_memo_id)
            except BookingMemo.DoesNotExist:
                invalid_memos.append({
                    "id": booking_memo_id,
                    "error": f"BookingMemo with id {booking_memo_id} does not exist."
                })
                continue

            # Check validations
            if booking_memo_instance.from_branch_id != from_branch:
                invalid_memos.append({
                    "id": booking_memo_id,
                    "error": "This booking memos's from_branch does not match the trip's from_branch."
                })
            if booking_memo_instance.vehical_no_id != vehicle_no:
                invalid_memos.append({
                    "id": booking_memo_id,
                    "error": "This booking memos's vehicle_no does not match the trip's vehicle_no."
                })
            # if booking_memo_instance.driver_name_id != driver_name:
            #     invalid_memos.append({
            #         "id": booking_memo_id,
            #         "error": "This booking memos's driver_name does not match the trip's driver_name."
            #     })
            else:
                # Validate if the booking memo is already linked to another active TripMemo
                linked_trip_memo = TripMemo.objects.filter(
                    booking_memos__booking_memo=booking_memo_instance,
                    is_active=True,
                    flag=True
                ).exclude(pk=trip_memo_id).first()

                if linked_trip_memo:
                    invalid_memos.append({
                        "id": booking_memo_id,
                        "error": "BookingMemo is already linked to another active TripMemo."
                    })
                else:
                    valid_booking_memo_ids.append(booking_memo_id)
               
        if invalid_memos:
            return Response({
                "message": "Validation errors in booking memos.",
                "status": "error",
                "errors": invalid_memos
            }, status=status.HTTP_400_BAD_REQUEST)

        try:          
            # Retrieve the TripMemo instance
            trip_memo_instance = get_object_or_404(TripMemo, pk=trip_memo_id)

            # Initialize serializer with the instance and updated data
            trip_memo_serializer = TripMemoSerializer(trip_memo_instance, data=request.data, partial=True)

            if trip_memo_serializer.is_valid():
                # Before saving, check if vehicle_no or driver_name have changed
                old_vehicle_no = trip_memo_instance.vehicle_no
                old_driver_name = trip_memo_instance.driver_name

                # Save the updated instance
                trip_memo_instance = trip_memo_serializer.save(updated_by=request.user)

                # Compare old and new vehicle_no and driver_name to update availability
                if old_vehicle_no != vehicle_no:
                    if old_vehicle_no:
                        old_vehicle_no.is_available = True
                        old_vehicle_no.save()

                    # Set new vehicle_no to unavailable
                    new_vehicle_instance = get_object_or_404(VehicalMaster, pk=vehicle_no)
                    new_vehicle_instance.is_available = False
                    new_vehicle_instance.save()

                # if old_driver_name != driver_name:
                #     if old_driver_name:
                #         old_driver_name.is_available = True
                #         old_driver_name.save()

                #     # Set new driver_name to unavailable
                #     new_driver_instance = get_object_or_404(DriverMaster, pk=driver_name)
                #     new_driver_instance.is_available = False
                #     new_driver_instance.save()

               
                if booking_memos_data is not None:                    
                    # Fetch existing booking memos linked to the instance
                    existing_booking_memos = list(trip_memo_instance.booking_memos.all())
                    
                    # If the list is empty, delete all existing booking memos
                    if not booking_memos_data:  # If no new booking memos are provided                       
                        for memo in existing_booking_memos:
                            memo.delete()
                        trip_memo_instance.booking_memos.clear()  # Clear the relation
                    else:                        
                        # Create a map of existing TripBokkingMemos IDs for quick lookup
                        existing_booking_memos_ids = {memo.id for memo in existing_booking_memos}

                        # Extract new BookingMemo IDs from the request
                        new_booking_memos_ids = {item.get('id') for item in booking_memos_data if item.get('id') != 0}                     
                        # Identify BookingMemo items to delete
                        booking_memos_to_delete = [memo for memo in existing_booking_memos if memo.id not in new_booking_memos_ids]

                        # Delete BookingMemo items that are no longer linked
                        for memo in booking_memos_to_delete:
                            memo.delete()                     
                        # Initialize lists to keep track of new and updated BookingMemos
                        booking_memos_to_add = []
                        booking_memos_to_update = []                       
                        for item in booking_memos_data:                           
                            # Check if the item has an ID
                            if item.get('id') == 0:  # New record                                
                                booking_memo_instance = get_object_or_404(BookingMemo, pk=item['booking_memo'])
                                new_booking_memo = TripBokkingMemos.objects.create(
                                    booking_memo=booking_memo_instance,
                                    remark=item.get('remark', ''),
                                    created_by=request.user
                                )
                                booking_memos_to_add.append(new_booking_memo)
                            else:  # Existing record                            
                                existing_booking_memo = get_object_or_404(TripBokkingMemos, pk=item['id'])                               
                                existing_booking_memo.booking_memo = get_object_or_404(BookingMemo, pk=item['booking_memo'])                           
                                existing_booking_memo.remark = item.get('remark', '')                             
                                existing_booking_memo.save()                        
                                booking_memos_to_update.append(existing_booking_memo)                            
                        # Now set the booking memos after the TripMemo instance has been saved
                        trip_memo_instance.booking_memos.set(booking_memos_to_add + booking_memos_to_update)
                        print("13")
                return Response({
                    'message': 'Trip Memo updated successfully',
                    'status': 'success',
                    'data': trip_memo_serializer.data
                }, status=status.HTTP_200_OK)

            return Response({
                'message': 'Failed to update Trip Memo',
                'status': 'error',
                'errors': trip_memo_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except TripMemo.DoesNotExist:
            return Response({
                'message': 'Trip Memo not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except BookingMemo.DoesNotExist:
            return Response({
                'message': 'Booking Memo not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class TripMemoUpdateView(APIView):
#     def post(self, request, *args, **kwargs):
#         # Extract ID from request data
#         trip_memo_id = request.data.get('id')

#         if not trip_memo_id:
#             return Response({
#                 'message': 'Trip Memo ID is required',
#                 'status': 'error',
#                 'data': {}
#             }, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Retrieve the TripMemo instance
#             trip_memo_instance = get_object_or_404(TripMemo, pk=trip_memo_id)

#             # Initialize serializer with the instance and updated data
#             trip_memo_serializer = TripMemoSerializer(trip_memo_instance, data=request.data, partial=True)

#             if trip_memo_serializer.is_valid():
#                 # Save the updated instance
#                 trip_memo_instance = trip_memo_serializer.save(updated_by=request.user)

#                 # Get the 'booking_memos' from the request
#                 booking_memos_data = request.data.get('booking_memos', [])

#                 if booking_memos_data:
#                     try:
#                         # Fetch existing booking memos linked to the instance
#                         existing_booking_memos = list(trip_memo_instance.booking_memos.all())
                        
#                         # Create a map of existing TripBokkingMemos IDs for quick lookup
#                         existing_booking_memos_ids = {memo.id for memo in existing_booking_memos}

#                         # Extract new BookingMemo IDs from the request
#                         new_booking_memos_ids = {item.get('id') for item in booking_memos_data if item.get('id') != 0}

#                         # Identify BookingMemo items to delete
#                         booking_memos_to_delete = [memo for memo in existing_booking_memos if memo.id not in new_booking_memos_ids]

#                         # Delete BookingMemo items that are no longer linked
#                         for memo in booking_memos_to_delete:
#                             memo.delete()

#                         # Initialize lists to keep track of new and updated BookingMemos
#                         booking_memos_to_add = []
#                         booking_memos_to_update = []

#                         for item in booking_memos_data:
#                             # Check if the item has an ID
#                             if item.get('id') == 0:  # New record
#                                 booking_memo_instance = get_object_or_404(BookingMemo, pk=item['booking_memo'])
#                                 new_booking_memo = TripBokkingMemos.objects.create(
#                                     booking_memo=booking_memo_instance,
#                                     remark=item.get('remark', ''),
#                                     created_by=request.user
#                                 )
#                                 booking_memos_to_add.append(new_booking_memo)
#                             else:  # Existing record
#                                 existing_booking_memo = get_object_or_404(TripBokkingMemos, pk=item['id'])
#                                 existing_booking_memo.booking_memo = get_object_or_404(BookingMemo, pk=item['booking_memo'])
#                                 existing_booking_memo.remark = item.get('remark', '')
#                                 existing_booking_memo.save()
#                                 booking_memos_to_update.append(existing_booking_memo)

#                         # Now set the booking memos after the TripMemo instance has been saved
#                         trip_memo_instance.booking_memos.set(booking_memos_to_add + booking_memos_to_update)
                    
#                     except BookingMemo.DoesNotExist:
#                         return Response({"error": "BookingMemo not found"}, status=status.HTTP_400_BAD_REQUEST)

#                 return Response({
#                     'message': 'Trip Memo updated successfully',
#                     'status': 'success',
#                     'data': trip_memo_serializer.data
#                 }, status=status.HTTP_200_OK)
            
#             return Response({
#                 'message': 'Failed to update Trip Memo',
#                 'status': 'error',
#                 'errors': trip_memo_serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         except TripMemo.DoesNotExist:
#             return Response({
#                 'message': 'Trip Memo not found',
#                 'status': 'error',
#                 'data': {}
#             }, status=status.HTTP_404_NOT_FOUND)

class TripMemoRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract 'id' from request data to identify the record to retrieve
        trip_memo_id = request.data.get('id')

        if trip_memo_id is None:
            return Response({
                "status": "error",
                "message": "No ID provided.",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the trip mode from the database
            trip_memo = TripMemo.objects.get(pk=trip_memo_id)
        except TripMemo.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Trip memo not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item data
        serializer = TripMemoSerializer(trip_memo)

        # Return a success response with the item data
        return Response({
            "status": "success",
            "message": "Trip memo retrieved successfully.",
            "data": [serializer.data]
        }, status=status.HTTP_200_OK)

class TripMemoRetrieveAllView(APIView):
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
            
            # Retrieve all active trip memos from the database
            items = TripMemo.objects.filter(
                flag=True
                ).filter(
                Q(branch__in=allowed_branches) | Q(from_branch__in=allowed_branches)  
                ).filter(
                Q(branch_id=branch_id) | Q(from_branch_id=branch_id)
                ).order_by('-id')

            # Serialize the items data
            serializer = TripMemoSerializer(items, many=True)

            # Return a success response with the items data
            return Response({
                "status": "success",
                "message": "Trip memos retrieved successfully.",
                "data": [serializer.data]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while retrieving the trip memos.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TripMemoRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all active trip memos from the database
            items = TripMemo.objects.filter(is_active=True, flag=True).order_by('-id')

            # Serialize the items data
            serializer = TripMemoSerializer(items, many=True)

            # Return a success response with the items data
            return Response({
                "status": "success",
                "message": "Active trip memos retrieved successfully.",
                "data": [serializer.data]
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while retrieving the active trip memos.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TripMemoFilterView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(TripMemo, filters)

            # Serialize the filtered data
            serializer = TripMemoSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class TripMemoSoftDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        trip_memo_id = request.data.get('id')

        if not trip_memo_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the TripMemo instance
            instance = TripMemo.objects.get(pk=trip_memo_id)

            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()

            return Response({
                'msg': 'Trip memo deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)

        except TripMemo.DoesNotExist:
            return Response({
                'msg': 'Trip memo not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class TripMemoPermanentDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        trip_memo_id = request.data.get('id')

        if not trip_memo_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the TripMemo instance
            instance = TripMemo.objects.get(pk=trip_memo_id)

            # Permanently delete the instance
            instance.delete()

            return Response({
                'msg': 'Trip memo permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)

        except TripMemo.DoesNotExist:
            return Response({
                'msg': 'Trip memo not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)



class BookingMemoPendingForTripMemoView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extracting the optional parameter from the request body
            from_branch_id = request.data.get('from_branch_id')

            # Filtering BookingMemo instances based on provided parameters and excluding those linked to TripBokkingMemos
            queryset = BookingMemo.objects.filter(is_active=True, flag=True).exclude(
                id__in=TripBokkingMemos.objects.values_list('booking_memo_id', flat=True)
            )

            # If from_branch_id is provided, filter by it, otherwise retrieve all
            if from_branch_id:
                queryset = queryset.filter(from_branch_id=from_branch_id)

            # Serialize the filtered queryset
            new_response_data = BookingMemoSerializer(queryset, many=True)

            # Return success response with serialized data
            return Response({
                'msg': 'Booking Memo retrieved successfully',
                'status': 'success',
                'data': new_response_data.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BookingMemoPendingForTURView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extracting the optional parameter from the request body
            to_branch_id = request.data.get('to_branch_id')

            # Filtering BookingMemo instances based on provided parameters and excluding those linked to TruckUnloadingReport
            queryset = BookingMemo.objects.filter(is_active=True, flag=True).exclude(
                id__in=TruckUnloadingReport.objects.values_list('memo_no_id', flat=True)
            )

            # valid_booking_memos = []
            # for memo in queryset:
            #     # Check if the memo is linked to any incomplete TripMemo
            #     linked_trip_memos = TripMemo.objects.filter(
            #         booking_memos__booking_memo=memo
            #     )
            #     # If any linked TripMemo is inactive or flagged, exclude it
            #     if not linked_trip_memos.filter(is_active=True, flag=True).exists():
            #         continue  # Skip this memo if any linked TripMemo is incomplete
            #     valid_booking_memos.append(memo)

            # If to_branch_id is provided, further filter the queryset by it
            if to_branch_id:
                filtered_queryset = [
                    memo_booking for memo_booking in queryset if memo_booking.to_branch_id == to_branch_id
                ]
            else:
                # If to_branch_id is not provided, return all valid memos
                filtered_queryset = queryset

            # Serialize the filtered queryset data
            new_response_data = BookingMemoSerializer(filtered_queryset, many=True)

            # Return success response with serialized data
            return Response({
                'msg': 'Booking Memo retrieved successfully',
                'status': 'success',
                'data': new_response_data.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BrokerMasterCreateView(APIView):        
    def post(self, request, *args, **kwargs):
        # Extracting trip details data from the request
        trip_details_data = request.data.get('trip_details', [])               
        owner_id = request.data.get("owner")
        
        if not trip_details_data:
            return Response({
                "message": "Trip Details data is required.",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)
        if not owner_id:
            return Response({
                "message": "Owner is a required field.",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():  # Ensure atomicity
                # Check if a BrokerMaster record already exists for the owner
                broker_master_instance, created = BrokerMaster.objects.get_or_create(
                    owner_id=owner_id, 
                    defaults={"created_by": request.user}
                )

                # Collect new trips to add to BrokerMasterTrips
                trip_details_to_add = []
                for item in trip_details_data:
                    trip_memo_id = item.get('trip_memo')
                    advance = item.get('advance', 0)

                    if not trip_memo_id:
                        raise ValidationError(f"Trip memo ID is required for all trip details.")

                    # Validate TripMemo existence
                    try:
                        trip_memo_instance = TripMemo.objects.get(pk=trip_memo_id)
                    except TripMemo.DoesNotExist:
                        raise ValidationError(f"TripMemo with id {trip_memo_id} does not exist.")

                    # Check for existing BrokerMasterTrips record
                    broker_trip_instance, trip_created = BrokerMasterTrips.objects.get_or_create(
                        trip_memo=trip_memo_instance,
                        defaults={"advance": advance, "created_by": request.user}
                    )

                    if not trip_created:  # Update advance if record exists
                        broker_trip_instance.advance = advance
                        broker_trip_instance.save()

                    trip_details_to_add.append(broker_trip_instance)

                # Add trips to BrokerMaster
                broker_master_instance.trip_details.add(*trip_details_to_add)

                # Serialize and return the BrokerMaster instance
                response_serializer = BrokerMasterSerializer(broker_master_instance)
                return Response({
                    "message": "Broker Master created/updated successfully!",
                    "status": "success",
                    "data": response_serializer.data
                }, status=status.HTTP_201_CREATED)
        except ValidationError as ve:
            return Response({
                "message": "Validation Error",
                "status": "error",
                "errors": str(ve)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "message": "An error occurred while processing the request.",
                "status": "error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BrokerMasterUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        owner_id = request.data.get("owner")
        trip_details_data = request.data.get("trip_details", [])

        # Validate the presence of required fields
        if not owner_id:
            return Response({
                "message": "Owner is required.",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)

        if not trip_details_data:
            return Response({
                "message": "Trip Details data is required.",
                "status": "error"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the BrokerMaster instance for the given owner
            broker_master_instance = BrokerMaster.objects.filter(owner_id=owner_id).first()

            if not broker_master_instance:
                return Response({
                    "message": "BrokerMaster for the given owner does not exist.",
                    "status": "error"
                }, status=status.HTTP_404_NOT_FOUND)

            # Start a transaction
            with transaction.atomic():
                # Retrieve current trip_details associated with the BrokerMaster
                existing_trip_details = list(broker_master_instance.trip_details.all())
                existing_trip_detail_ids = {trip.id for trip in existing_trip_details}

                # Process the incoming trip details
                new_trip_details = []
                for item in trip_details_data:
                    trip_memo_id = item.get('trip_memo')
                    advance = item.get('advance', 0)

                    if not trip_memo_id:
                        return Response({
                            "message": "Each trip detail must include a trip_memo ID.",
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)

                    try:
                        # Fetch the TripMemo instance
                        trip_memo_instance = TripMemo.objects.get(pk=trip_memo_id)
                    except TripMemo.DoesNotExist:
                        return Response({
                            "message": f"TripMemo with ID {trip_memo_id} does not exist.",
                            "status": "error"
                        }, status=status.HTTP_400_BAD_REQUEST)

                    # Check if this trip already exists in BrokerMasterTrips
                    broker_master_trip_instance = BrokerMasterTrips.objects.filter(
                        trip_memo=trip_memo_instance,
                        id__in=existing_trip_detail_ids
                    ).first()

                    if broker_master_trip_instance:
                        # Update the existing trip's advance
                        broker_master_trip_instance.advance = advance
                        broker_master_trip_instance.save()
                        existing_trip_detail_ids.remove(broker_master_trip_instance.id)
                    else:
                        # Create a new BrokerMasterTrips instance
                        broker_master_trip_instance = BrokerMasterTrips.objects.create(
                            trip_memo=trip_memo_instance,
                            advance=advance,
                            created_by=request.user
                        )

                    new_trip_details.append(broker_master_trip_instance)

                # Remove trip details not included in the request
                trips_to_remove = BrokerMasterTrips.objects.filter(
                    id__in=existing_trip_detail_ids
                )
                trips_to_remove.delete()

                # Update the BrokerMaster instance with the new trip details
                broker_master_instance.trip_details.set(new_trip_details)
                broker_master_instance.updated_by = request.user
                broker_master_instance.save()

                # Serialize and return the updated BrokerMaster instance
                response_serializer = BrokerMasterSerializer(broker_master_instance)
                return Response({
                    "message": "BrokerMaster updated successfully!",
                    "status": "success",
                    "data": response_serializer.data
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'message': 'An error occurred during the update process.',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BrokerMasterRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract 'id' from request data to identify the record to retrieve
        owner_id = request.data.get('owner')

        if owner_id is None:
            return Response({
                "status": "error",
                "message": "No owner_id provided.",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the trip mode from the database
            trip_memo = BrokerMaster.objects.get(owner_id=owner_id)
        except BrokerMaster.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Broker Master not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item data
        serializer = BrokerMasterSerializer(trip_memo)

        # Return a success response with the item data
        return Response({
            "status": "success",
            "message": "Broker Master retrieved successfully.",
            "data": [serializer.data]
        }, status=status.HTTP_200_OK)

class BrokerMasterRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = BrokerMaster.objects.filter(flag=True).order_by('-id')

            # Serialize the items data
            serializer = BrokerMasterSerializer(items, many=True)

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

class BrokerMasterRetrieveActiveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = BrokerMaster.objects.filter(flag=True,is_active=True).order_by('-id')

            # Serialize the items data
            serializer = BrokerMasterSerializer(items, many=True)

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

class BrokerMasterSoftDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        broker_master_id = request.data.get('id')

        if not broker_master_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the TripMemo instance
            instance = BrokerMaster.objects.get(pk=broker_master_id)

            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()

            return Response({
                'msg': 'Broker Master deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)

        except BrokerMaster.DoesNotExist:
            return Response({
                'msg': 'Broker Master not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
