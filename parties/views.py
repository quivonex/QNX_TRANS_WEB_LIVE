from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import PartyTypes, PartyMaster
from .serializers import PartyTypesSerializer, PartyMasterSerializer
from rest_framework.exceptions import ValidationError
from company.filters import apply_filters

# Create View for PartyTypes
class PartyTypesCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the data from the request
            serializer = PartyTypesSerializer(data=request.data)
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                # Return success response with the serialized data
                return Response({
                    'status': 'success',
                    'message': 'PartyTypes created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Failed to create PartyTypes',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# Retrieve View for PartyTypes
class PartyTypesRetrieveAPIView(APIView):
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
            # Retrieve the PartyTypes instance
            instance = PartyTypes.objects.get(pk=effect_type_id)
            serializer = PartyTypesSerializer(instance)
            
            response_data = {
                'msg': 'PartyTypes retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except PartyTypes.DoesNotExist:
            return Response({
                'msg': 'PartyTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
                
# Retrieve All View for PartyTypes
class PartyTypesListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of PartyTypes
            instances = PartyTypes.objects.filter(flag=True).order_by('-id')

            serializer = PartyTypesSerializer(instances, many=True)
            
            response_data = {
                'msg': 'PartyTypes retrieved successfully',
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
    
class PartyTypesRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve active PartyTypes
            queryset = PartyTypes.objects.filter(is_active=True,flag=True)
            serializer = PartyTypesSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'PartyTypes retrieved successfully',
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
    
    
class PartyTypesUpdateAPIView(APIView):
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
            # Retrieve the PartyTypes instance
            instance = PartyTypes.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = PartyTypesSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'PartyTypes updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update PartyTypes',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except PartyTypes.DoesNotExist:
            return Response({
                'msg': 'PartyTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class PartyTypesSoftDeleteAPIView(APIView):
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
            # Retrieve the PartyTypes instance
            instance = PartyTypes.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'PartyTypes deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except PartyTypes.DoesNotExist:
            return Response({
                'msg': 'PartyTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class PartyTypesPermanentDeleteAPIView(APIView):
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
            # Retrieve the PartyTypes instance
            instance = PartyTypes.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'PartyTypes permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except PartyTypes.DoesNotExist:
            return Response({
                'msg': 'PartyTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
                  
# Create View for PartyMaster
class PartyMasterCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the data from the request
            serializer = PartyMasterSerializer(data=request.data)
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                # Return success response with the serialized data
                return Response({
                    'status': 'success',
                    'message': 'PartyMaster created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Failed to create PartyMaster.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# Retrieve View for PartyMaster
class PartyMasterRetrieveAPIView(APIView):
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
            # Retrieve the PartyMaster instance
            instance = PartyMaster.objects.get(pk=effect_type_id)
            serializer = PartyMasterSerializer(instance)
            
            response_data = {
                'msg': 'PartyMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except PartyMaster.DoesNotExist:
            return Response({
                'msg': ' PartyMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
# Retrieve All View for PartyMaster
class PartyMasterListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of PartyMaster
            instances = PartyMaster.objects.filter(flag=True).order_by('-id')

            serializer = PartyMasterSerializer(instances, many=True)
            
            response_data = {
                'msg': 'PartyMaster retrieved successfully',
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
    
class PartyMasterRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all active PartyMaster instances
            queryset = PartyMaster.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = PartyMasterSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'PartyMaster retrieved successfully',
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

class PartyMasterRetrieveForPartyBillingView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all active PartyMaster instances
            queryset = PartyMaster.objects.filter(is_active=True,flag=True,party_type_id=2).order_by('-id')
            serializer = PartyMasterSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'PartyMaster retrieved successfully',
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

class PartyMasterRetrieveByBranchView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve the branch_id from the request data
            branch_id = request.data.get('branch_id')

            if not branch_id:
                return Response({
                    'status': 'error',
                    'message': 'branch_id is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Filter PartyMaster by active status, flag, and branch_id
            queryset = PartyMaster.objects.filter(is_active=True, flag=True, branch__id=branch_id).order_by('-id')
            
            if not queryset.exists():
                return Response({
                    'status': 'error',
                    'message': f'No PartyMaster found for branch_id {branch_id}'
                }, status=status.HTTP_404_NOT_FOUND)

            # Serialize the queryset
            serializer = PartyMasterSerializer(queryset, many=True)

            response_data = {
                'msg': 'PartyMaster retrieved successfully',
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

class PartyMasterFilterView(APIView): 
    def post(self, request, *args, **kwargs):        
        try:       
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(PartyMaster, filters)

            # Serialize the filtered data
            serializer = PartyMasterSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class PartyMasterUpdateAPIView(APIView):
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
            # Retrieve the PartyMaster instance
            instance = PartyMaster.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = PartyMasterSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'PartyMaster updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update PartyMaster',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except PartyMaster.DoesNotExist:
            return Response({
                'msg': 'PartyMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

class PartyMasterSoftDeleteAPIView(APIView):
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
            # Retrieve the PartyMaster instance
            instance = PartyMaster.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'PartyMaster deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except PartyMaster.DoesNotExist:
            return Response({
                'msg': 'PartyMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class PartyMasterPermanentDeleteAPIView(APIView):
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
            # Retrieve the PartyMaster instance
            instance = PartyMaster.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'PartyMaster permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except PartyMaster.DoesNotExist:
            return Response({
                'msg': 'PartyMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
