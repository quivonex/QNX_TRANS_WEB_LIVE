from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import EffectTypes, PaymentTypes, ReceiptTypes, User
from .serializers import EffectTypesSerializer, PaymentTypesSerializer,  ReceiptTypesSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from company.filters import apply_filters

class EffectTypesCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the data from the request
            serializer = EffectTypesSerializer(data=request.data)
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                # Return success response with the serialized data
                response_data = {
                    'status': 'success',
                    'message': 'Effect Type created successfully.',
                    'data': [serializer.data]
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Failed to create Effect Type.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating Effect Type.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class EffectTypesRetrieveView(APIView):
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
            # Retrieve the EffectTypes instance
            instance = EffectTypes.objects.get(pk=effect_type_id)
            serializer = EffectTypesSerializer(instance)
            
            response_data = {
                'msg': 'Effect type retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except EffectTypes.DoesNotExist:
            return Response({
                'msg': 'Effect type not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class EffectTypesRetrieveAllView(APIView):
    permission_classes = [AllowAny]  # Adjust if authentication is needed

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of EffectTypes
            instances = EffectTypes.objects.filter(flag=True).order_by('-id')
            serializer = EffectTypesSerializer(instances, many=True)
            
            response_data = {
                'msg': 'Effect types retrieved successfully',
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
        

class EffectTypesRetrieveFilteredView(APIView):
    permission_classes = [AllowAny]  # Adjust if authentication is needed

    def post(self, request, *args, **kwargs):
        try:
            # Extract filter value for is_active from request data
            is_active = request.data.get('is_active', True)  # Default to True if not provided
            
            # Filter instances based on is_active value
            queryset = EffectTypes.objects.filter(is_active=is_active,flag=True).order_by('-id')
            serializer = EffectTypesSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'Effect types retrieved successfully',
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
        
    
class EffectTypesUpdateAPIView(APIView):
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
            # Retrieve the EffectTypes instance
            instance = EffectTypes.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = EffectTypesSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'EffectTypes updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update EffectTypes',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except EffectTypes.DoesNotExist:
            return Response({
                'msg': 'EffectTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class EffectTypesSoftDeleteAPIView(APIView):
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
            # Retrieve the EffectTypes instance
            instance = EffectTypes.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'EffectTypes deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except EffectTypes.DoesNotExist:
            return Response({
                'msg': 'EffectTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class EffectTypesPermanentDeleteAPIView(APIView):
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
            # Retrieve the EffectTypes instance
            instance = EffectTypes.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'EffectTypes permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except EffectTypes.DoesNotExist:
            return Response({
                'msg': 'EffectTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)


class PaymentTypesCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the data from the request
            serializer = PaymentTypesSerializer(data=request.data)
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                
                # Return success response with the serialized data
                return Response({
                    'status': 'success',
                    'message': 'Payment Type created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Failed to create Payment Type.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating Payment Type.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class PaymentTypesRetrieveView(APIView):
    permission_classes = [AllowAny]  # Adjust if authentication is needed

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
            instance = PaymentTypes.objects.get(pk=payment_type_id)
            serializer =  PaymentTypesSerializer(instance)
            
            response_data = {
                'msg': ' PaymentType retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except  PaymentTypes.DoesNotExist:
            return Response({
                'msg': ' PaymentTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class PaymentTypesRetrieveAllView(APIView):
    permission_classes = [AllowAny]  # Adjust if authentication is needed

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of PaymentTypes
            instances = PaymentTypes.objects.filter(flag=True).order_by('-id')

            serializer = PaymentTypesSerializer(instances, many=True)
            
            # Create a custom response
            response_data = {
                'msg': 'Payment types retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving Payment Types.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class PaymentTypesRetrieveFilteredView(APIView):
    permission_classes = [AllowAny]  # Adjust if authentication is needed

    def post(self, request, *args, **kwargs):
        try:
            # Extract filter value for is_active from request data
            # You can add more filters based on request data if needed
            queryset = PaymentTypes.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = PaymentTypesSerializer(queryset, many=True)
            
            # Create a custom response
            response_data = {
                'msg': 'PaymentTypes retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving Payment Types.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class PaymentTypesUpdateAPIView(APIView):
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
            # Retrieve the PaymentTypes instance
            instance = PaymentTypes.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = PaymentTypesSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'PaymentTypes updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update PaymentTypes',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except PaymentTypes.DoesNotExist:
            return Response({
                'msg': 'PaymentTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class PaymentTypesSoftDeleteAPIView(APIView):
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
            # Retrieve the PaymentTypes instance
            instance = PaymentTypes.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'PaymentTypes deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except PaymentTypes.DoesNotExist:
            return Response({
                'msg': 'PaymentTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class PaymentTypesPermanentDeleteAPIView(APIView):
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
            # Retrieve the PaymentTypes instance
            instance = PaymentTypes.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'PaymentTypes permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except PaymentTypes.DoesNotExist:
            return Response({
                'msg': 'PaymentTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

    
class ReceiptTypesCreateView(APIView):
    permission_classes = [AllowAny]  # Adjust if authentication is needed

    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the request data
            serializer = ReceiptTypesSerializer(data=request.data)
            
            # Validate the serializer
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                
                # Create a custom response
                response_data = {
                    'msg': 'Receipt type created successfully',
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
                'status': 'error',
                'message': 'An error occurred while creating Receipt Type.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class ReceiptTypesRetrieveView(APIView):
    permission_classes = [AllowAny]  # Adjust if authentication is needed

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
            instance = ReceiptTypes.objects.get(pk=receipt_type_id)
            serializer = ReceiptTypesSerializer(instance)
            
            response_data = {
                'msg': 'Receipt type retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except ReceiptTypes.DoesNotExist:
            return Response({
                'msg': 'Receipt type not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)


class ReceiptTypesRetrieveAllView(APIView):
    permission_classes = [AllowAny]  # Adjust if authentication is needed

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of ReceiptTypes
            instances = ReceiptTypes.objects.filter(flag=True).order_by('-id')

            serializer = ReceiptTypesSerializer(instances, many=True)
            
            response_data = {
                'msg': 'Receipt types retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving Receipt Types.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class ReceiptTypesRetrieveFilteredView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Filter instances of ReceiptTypes based on is_active field
            queryset = ReceiptTypes.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = ReceiptTypesSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'Receipt types retrieved successfully',
                'status': 'success',
                'data':[serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving Receipt Types.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class ReceiptTypesUpdateAPIView(APIView):
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
            # Retrieve the ReceiptTypes instance
            instance = ReceiptTypes.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = ReceiptTypesSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'ReceiptTypes updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update ReceiptTypes',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ReceiptTypes.DoesNotExist:
            return Response({
                'msg': 'ReceiptTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ReceiptTypesSoftDeleteAPIView(APIView):
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
            # Retrieve the ReceiptTypes instance
            instance = ReceiptTypes.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'ReceiptTypes deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except ReceiptTypes.DoesNotExist:
            return Response({
                'msg': 'ReceiptTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class ReceiptTypesPermanentDeleteAPIView(APIView):
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
            instance = ReceiptTypes.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'ReceiptTypes permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except ReceiptTypes.DoesNotExist:
            return Response({
                'msg': 'ReceiptTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
