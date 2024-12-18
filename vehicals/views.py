from django.shortcuts import render

# Create your views here.
# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from collection.models import TripMemo
from collection.serializers import TripMemoSerializer
from .models import OwnerMaster, VehicalTypes, VendorTypes, VehicalMaster, DriverMaster
from .serializers import OwnerMasterSerializer, VehicalTypesSerializer, VendorTypesSerializer, VehicalMasterSerializer, DriverMasterSerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.exceptions import ValidationError
from company.filters import apply_filters

def send_test_email():   
    subject = 'Test Email'
    message = 'This is a test email sent from Django.'
    from_email = settings.EMAIL_HOST_USER    
    recipient_list = ['innovatrixt@gmail.com']

    try:       
        send_mail(subject, message, from_email, recipient_list)
        print("Email sent successfully.")
    except Exception as e:  
        print(f"Failed to send email: {e}")
    return True

class EmailAPIView(APIView):
    def post(self, request, *args, **kwargs):
        if send_test_email() :
            return Response({
                    'status': 'success',
                    'message': 'mail created successfully.'                    
                }, status=status.HTTP_201_CREATED)

         

# OwnerMaster Views
class OwnerMasterCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the data from the request
            serializer = OwnerMasterSerializer(data=request.data)
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                # Return success response with the serialized data
                return Response({
                    'status': 'success',
                    'message': 'OwnerMaster created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Failed to create OwnerMaster.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle unexpected errors
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred.',
                'errors': str(e)  # Convert the exception to a string
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
 
class OwnerMasterRetrieveAPIView(APIView):
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
            # Retrieve the OwnerMaster instance
            instance = OwnerMaster.objects.get(pk=effect_type_id)
            serializer = OwnerMasterSerializer(instance)
            
            response_data = {
                'msg': 'OwnerMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except OwnerMaster.DoesNotExist:
            return Response({
                'msg': 'OwnerMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class OwnerMasterListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of OwnerMaster
            instances = OwnerMaster.objects.filter(flag=True).order_by('-id')
            serializer = OwnerMasterSerializer(instances, many=True)
            
            response_data = {
                'msg': 'OwnerMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle unexpected errors
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred.',
                'errors': str(e)  # Convert the exception to a string
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class OwnerMasterFilterView(APIView): 
    def post(self, request, *args, **kwargs):        
        try:       
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(OwnerMaster, filters)

            # Serialize the filtered data
            serializer = OwnerMasterSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)        
        
class OwnerMasterActiveListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all active instances of OwnerMaster
            queryset = OwnerMaster.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = OwnerMasterSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'OwnerMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle unexpected errors
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred.',
                'errors': str(e)  # Convert the exception to a string
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
    
class OwnerMasterUpdateAPIView(APIView):
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
            # Retrieve the OwnerMaster instance
            instance = OwnerMaster.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = OwnerMasterSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'OwnerMaster updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
                
            return Response({
                'msg': 'Failed to update OwnerMaster',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except OwnerMaster.DoesNotExist:
            return Response({
                'msg': 'OwnerMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class OwnerMasterSoftDeleteAPIView(APIView):
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
            # Retrieve the OwnerMaster instance
            instance = OwnerMaster.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'OwnerMaster deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except OwnerMaster.DoesNotExist:
            return Response({
                'msg': 'OwnerMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)        

class OwnerMasterPermanentDeleteAPIView(APIView):
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
            # Retrieve the OwnerMaster instance
            instance = OwnerMaster.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'OwnerMaster permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except OwnerMaster.DoesNotExist:
            return Response({
                'msg': 'OwnerMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
          

# VehicalTypes Views
class VehicalTypesCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the request data
            serializer = VehicalTypesSerializer(data=request.data)
            
            # Validate the serializer
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                
                # Create a custom response
                response_data = {
                    'msg': 'VendorTypes created successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                # Return validation errors with a custom response
                response_data = {
                    'msg': 'Validation failed',
                    'status': 'error',
                    'data': serializer.errors
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle unexpected errors
            return Response({
                'msg': 'An unexpected error occurred.',
                'status': 'error',
                'error': str(e)  # Capture the exception as a string for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
class VehicalTypesRetrieveAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        payment_type_id = request.data.get('id')
        
        if not payment_type_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the EffectTypes instance
            instance = VehicalTypes.objects.get(pk=payment_type_id)
            serializer =  VehicalTypesSerializer(instance)
           
            response_data = {
                'msg': ' PaymentType retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except  VehicalTypes.DoesNotExist:
            return Response({
                'msg': ' VehicalTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)        

class VehicalTypesListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of VehicalTypes
            instances = VehicalTypes.objects.filter(flag=True).order_by('-id')

            serializer = VehicalTypesSerializer(instances, many=True)
            
            response_data = {
                'msg': 'VehicalTypes retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle unexpected errors
            return Response({
                'msg': 'An unexpected error occurred while retrieving VehicalTypes.',
                'status': 'error',
                'error': str(e)  # Capture the exception as a string for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VehicalTypesActiveListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all active instances of VehicalTypes
            queryset = VehicalTypes.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = VehicalTypesSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'VehicalTypes retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'msg': 'An error occurred while retrieving VehicalTypes.',
                'status': 'error',
                'error': str(e)  # Capture the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VehicalTypesUpdateAPIView(APIView):
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
            # Retrieve the VehicalTypes instance
            instance = VehicalTypes.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = VehicalTypesSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'VehicalTypes updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update VehicalTypes',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except VehicalTypes.DoesNotExist:
            return Response({
                'msg': 'VehicalTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VehicalTypesSoftDeleteAPIView(APIView):
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
            # Retrieve the VehicalTypes instance
            instance = VehicalTypes.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'VehicalTypes deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except VehicalTypes.DoesNotExist:
            return Response({
                'msg': 'VehicalTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
    
class VehicalTypesPermanentDeleteAPIView(APIView):
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
            # Retrieve the VehicalTypes instance
            instance = VehicalTypes.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'VehicalTypes permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except VehicalTypes.DoesNotExist:
            return Response({
                'msg': 'VehicalTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
         

# VendorTypes Views
class VendorTypesCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the request data
            serializer = VendorTypesSerializer(data=request.data)
            
            # Validate the serializer
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                
                # Create a custom response
                response_data = {
                    'msg': 'VendorTypes created successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                # Return validation errors with a custom response
                response_data = {
                    'msg': 'Validation failed',
                    'status': 'error',
                    'data': serializer.errors
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'msg': 'An error occurred while creating VendorTypes.',
                'status': 'error',
                'error': str(e)  # Capture the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
               
class VendorTypesRetrieveAPIView(APIView):
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
            # Retrieve the ReceiptTypes instance
            instance = VendorTypes.objects.get(pk=receipt_type_id)
            serializer = VendorTypesSerializer(instance)
            
            response_data = {
                'msg': 'VendorTypes retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except VendorTypes.DoesNotExist:
            return Response({
                'msg': 'VendorTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class VendorTypesListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of VendorTypes
            instances = VendorTypes.objects.filter(flag=True).order_by('-id')

            serializer = VendorTypesSerializer(instances, many=True)
            
            response_data = {
                'msg': 'VendorTypes retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'msg': 'An error occurred while retrieving VendorTypes.',
                'status': 'error',
                'error': str(e)  # Capture the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class VendorTypesActiveListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Filter VendorTypes where is_active is True
            queryset = VendorTypes.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = VendorTypesSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'VendorTypes retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'msg': 'An error occurred while retrieving VendorTypes.',
                'status': 'error',
                'error': str(e)  # Capture the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
class VendorTypesUpdateAPIView(APIView):
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
            # Retrieve the VendorTypes instance
            instance = VendorTypes.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = VendorTypesSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'VendorTypes updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update VendorTypes',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except VendorTypes.DoesNotExist:
            return Response({
                'msg': 'VendorTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VendorTypesSoftDeleteAPIView(APIView):
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
            # Retrieve the VendorTypes instance
            instance = VendorTypes.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'VendorTypes deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except VendorTypes.DoesNotExist:
            return Response({
                'msg': 'VendorTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class VendorTypesPermanentDeleteAPIView(APIView):
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
            # Retrieve the VendorTypes instance
            instance = VendorTypes.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'VendorTypes permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except VendorTypes.DoesNotExist:
            return Response({
                'msg': 'VendorTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
         

# VehicalMaster Views
class VehicalMasterCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        print(request.data)
        try:
            print(request)
            print(request.data)
            # Initialize the serializer with the data from the request
            serializer = VehicalMasterSerializer(data=request.data)
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                # Return success response with the serialized data               
                return Response({
                    'status': 'success',
                    'message': 'VehicalMaster created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Failed to create VehicalMaster.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating VehicalMaster.',
                'error': str(e)  # Capture the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VehicalMasterRetrieveAPIView(APIView):
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
            # Retrieve the VehicalMaster instance
            instance = VehicalMaster.objects.get(pk=effect_type_id)
            serializer = VehicalMasterSerializer(instance, context={'request': request})
            
            response_data = {
                'msg': 'VehicalMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except VehicalMaster.DoesNotExist:
            return Response({
                'msg': 'VehicalMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class VehicalMasterListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of VehicalMaster
            instances = VehicalMaster.objects.filter(flag=True).order_by('-id')

            serializer = VehicalMasterSerializer(instances, many=True, context={'request': request})

            response_data = {
                'msg': 'VehicalMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving VehicalMaster.',
                'error': str(e)  # Capture the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
    
class VehicalMasterActiveListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve instances of VehicalMaster where is_active is True
            queryset = VehicalMaster.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = VehicalMasterSerializer(queryset, many=True, context={'request': request})
            
            response_data = {
                'msg': 'VehicalMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving VehicalMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VehicalMasterFilterView(APIView): 
    def post(self, request, *args, **kwargs):        
        try:       
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(VehicalMaster, filters)

            # Serialize the filtered data
            serializer = VehicalMasterSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class CheckVehicleStatusView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract vehicle ID from the request
            vehicle_id = request.data.get('vehicle_id')
            if not vehicle_id:
                return Response({
                    "status": "error",
                    "msg": "Vehicle ID is required.",
                    "data": 0
                }, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the vehicle object
            try:
                vehicle = VehicalMaster.objects.get(id=vehicle_id)
            except VehicalMaster.DoesNotExist:
                return Response({
                    "status": "error",
                    "msg": "Vehicle not found.",
                    "data": 0
                }, status=status.HTTP_404_NOT_FOUND)

            # Check vehicle availability
            if vehicle.is_available:
                return Response({
                    "status": "success",
                    "msg": "This vehicle is available.",
                    "data": 0
                }, status=status.HTTP_200_OK)

            # If not available, check TripMemo
            trip_memo = TripMemo.objects.filter(
                vehicle_no=vehicle,
                trip_mode='OPEN',
                is_active=True,
                flag=True
            ).first()
            serializer = TripMemoSerializer(trip_memo)
            if trip_memo:
                return Response({
                    "status": "error",
                    "msg": f"The vehicle with number {vehicle.vehical_number} is currently on Trip {trip_memo.trip_no}, traveling from {trip_memo.from_branch.branch_name} to {trip_memo.to_branch.branch_name}.",
                    "data": [serializer.data]
                }, status=status.HTTP_400_BAD_REQUEST)

            # Default error message if no trip found but vehicle is not available
            return Response({
                "status": "error",
                "msg": "This vehicle is not available and no related trip found.",
                "data": 0
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": "error",
                "msg": "An unexpected error occurred.",
                "data": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VehicalMasterUpdateAvailableView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        driver_master_id = request.data.get('id')
        driver_master_is_available = request.data.get('is_available')
       
        if not driver_master_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the VehicalMaster instance
            instance = VehicalMaster.objects.get(pk=driver_master_id)
            
             # Update only the is_available field
            instance.is_available = driver_master_is_available
            instance.updated_by = request.user
            instance.save()
            
            return Response({
                'msg': 'VehicalMaster availability updated successfully',
                'status': 'success',
                'data': {'id': instance.id, 'is_available': instance.is_available}
            }, status=status.HTTP_200_OK)
        
        except VehicalMaster.DoesNotExist:
            return Response({
                'msg': 'VehicalMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VehicalMasterUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract ID from request data
        driver_master_id = request.data.get('id')
        print(request.data)
        if not driver_master_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the VehicalMaster instance
            instance = VehicalMaster.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = VehicalMasterSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'VehicalMaster updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update VehicalMaster',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except VehicalMaster.DoesNotExist:
            return Response({
                'msg': 'VehicalMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class VehicalMasterSoftDeleteAPIView(APIView):
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
            # Retrieve the VehicalMaster instance
            instance = VehicalMaster.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'VehicalMaster deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except VehicalMaster.DoesNotExist:
            return Response({
                'msg': 'VehicalMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
    
class VehicalMasterPermanentDeleteAPIView(APIView):
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
            # Retrieve the VehicalMaster instance
            instance = VehicalMaster.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'VehicalMaster permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except VehicalMaster.DoesNotExist:
            return Response({
                'msg': 'VehicalMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)            

# DriverMaster Views
class DriverMasterCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the data from the request
            serializer = DriverMasterSerializer(data=request.data)
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save()
                # Return success response with the serialized data
                return Response({
                    'status': 'success',
                    'message': 'DriverMaster created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Failed to create DriverMaster.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle unexpected errors
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred.',
                'errors': str(e)  # Convert the exception to a string
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
class DriverMasterRetrieveAPIView(APIView):
    def post(self, request, *args, **kwargs):
         # Extract ID from request data
        payment_type_id = request.data.get('id')
        
        if not payment_type_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the DriverMaster instance
            instance = DriverMaster.objects.get(pk=payment_type_id)
            serializer =  DriverMasterSerializer(instance)
            
            response_data = {
                'msg': 'DriverMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except  DriverMaster.DoesNotExist:
            return Response({
                'msg': 'DriverMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
            
class DriverMasterListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of DriverMaster
            instances = DriverMaster.objects.filter(flag=True).order_by('-id')

            serializer = DriverMasterSerializer(instances, many=True)
            
            response_data = {
                'msg': 'DriverMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle unexpected errors
            response_data = {
                'msg': 'An error occurred while retrieving DriverMaster',
                'status': 'error',
                'errors': str(e)  # Convert the exception to a string
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DriverMasterActiveListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all active instances of DriverMaster
            # queryset = DriverMaster.objects.filter(is_available=True,is_active=True,flag=True).order_by('-id')
            queryset = DriverMaster.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = DriverMasterSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'DriverMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle unexpected errors
            response_data = {
                'msg': 'An error occurred while retrieving DriverMaster',
                'status': 'error',
                'errors': str(e)  # Convert the exception to a string
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DriverMasterFilterView(APIView): 
    def post(self, request, *args, **kwargs):        
        try:       
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(DriverMaster, filters)

            # Serialize the filtered data
            serializer = DriverMasterSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class CheckDriverStatusView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract driver ID from the request
            driver_id = request.data.get('driver_id')
            if not driver_id:
                return Response({
                    "status": "error",
                    "msg": "Driver ID is required.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the driver object
            try:
                driver = DriverMaster.objects.get(id=driver_id)
            except DriverMaster.DoesNotExist:
                return Response({
                    "status": "error",
                    "msg": "Driver not found.",
                    "data": None
                }, status=status.HTTP_404_NOT_FOUND)

            # Check driver availability
            if driver.is_available:
                return Response({
                    "status": "success",
                    "msg": "This driver is available.",
                    "data": None
                }, status=status.HTTP_200_OK)

            # If not available, check TripMemo
            trip_memo = TripMemo.objects.filter(
                driver_name_id=driver,
                trip_mode='OPEN',
                is_active=True,
                flag=True
            ).first()

            if trip_memo:
                return Response({
                    "status": "error",
                    "msg": f"Trip {trip_memo.trip_no} is open with the selected driver.",
                    "data": None
                }, status=status.HTTP_400_BAD_REQUEST)

            # Default error message if no trip found but driver is not available
            return Response({
                "status": "error",
                "msg": "This driver is not available and no related trip found.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": "error",
                "msg": "An unexpected error occurred.",
                "data": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DriverMasterUpdateAvailableView(APIView):
    def post(self, request, *args, **kwargs):        
        # Extract ID from request data
        driver_master_id = request.data.get('id')
        driver_master_is_available = request.data.get('is_available')
        if not driver_master_id:
            return Response({
                'msg': 'ID and is_available required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Retrieve the DriverMaster instance
            instance = DriverMaster.objects.get(pk=driver_master_id)
            
             # Update only the is_available field
            instance.is_available = driver_master_is_available
            instance.updated_by = request.user
            instance.save()
            
            return Response({
                'msg': 'DriverMaster availability updated successfully',
                'status': 'success',
                'data': {'id': instance.id, 'is_available': instance.is_available}
            }, status=status.HTTP_200_OK)
        
        except DriverMaster.DoesNotExist:
            return Response({
                'msg': 'DriverMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DriverMasterUpdateAPIView(APIView):
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
            # Retrieve the DriverMaster instance
            instance = DriverMaster.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = DriverMasterSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'DriverMaster updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update DriverMaster',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except DriverMaster.DoesNotExist:
            return Response({
                'msg': 'DriverMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DriverMasterSoftDeleteAPIView(APIView):
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
            # Retrieve the DriverMaster instance
            instance = DriverMaster.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'DriverMaster deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except DriverMaster.DoesNotExist:
            return Response({
                'msg': 'DriverMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class DriverMasterPermanentDeleteAPIView(APIView):
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
            # Retrieve the DriverMaster instance
            instance = DriverMaster.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'DriverMaster permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except DriverMaster.DoesNotExist:
            return Response({
                'msg': 'DriverMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
 