from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from company.models import RegionMaster, StateMaster
from .models import BranchMaster, EmployeeType, EmployeeMaster
from .serializers import BranchMasterSerializer, EmployeeTypeSerializer, EmployeeMasterSerializer
from rest_framework.exceptions import ValidationError
from company.filters import apply_filters

# Create View for BranchMaster
class BranchMasterCreateAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the data from the request
            serializer = BranchMasterSerializer(data=request.data)
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                # Return success response with the serialized data
                return Response({
                    'status': 'success',
                    'message': 'BranchMaster created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Failed to create BranchMaster.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating BranchMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
# Retrieve View for BranchMaster
class BranchMasterRetrieveAPIView(APIView):
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
            # Retrieve the BranchMaster instance
            instance = BranchMaster.objects.get(pk=effect_type_id)
            serializer = BranchMasterSerializer(instance)
            
            response_data = {
                'msg': 'BranchMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except BranchMaster.DoesNotExist:
            return Response({
                'msg': 'Effect type not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class BranchStateRetrieveAPIView(APIView):
    def post(self, request, *args, **kwargs):
        branch_id = request.data.get('id')
        
        if not branch_id:
            return Response({
                'msg': 'ID is required',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the BranchMaster instance
            branch_instance = BranchMaster.objects.get(pk=branch_id)
            region_instance = branch_instance.region  # Get related RegionMaster instance
            state_instance = region_instance.state  # Get related StateMaster instance
            
            # Prepare response data
            state_data = {
                'id': state_instance.id,
                'state_name': state_instance.state_name,
                'state_code': state_instance.state_code,
            }

            response_data = {
                'msg': 'StateMaster retrieved successfully',
                'status': 'success',
                'data': state_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except BranchMaster.DoesNotExist:
            return Response({
                'msg': 'Branch not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                'msg': str(e),
                'status': 'error',
                'data': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# Retrieve All View for BranchMaster
class BranchMasterListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of BranchMaster
            instances = BranchMaster.objects.filter(flag=True).order_by('-id')
            serializer = BranchMasterSerializer(instances, many=True)
            
            response_data = {
                'msg': 'BranchMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving BranchMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
# Active BranchMaster List View
class ActiveBranchMasterListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Extract filter value for is_active
            queryset = BranchMaster.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = BranchMasterSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'Active BranchMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving active BranchMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BranchMasterFilterView(APIView): 
    def post(self, request, *args, **kwargs):        
        try:       
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(BranchMaster, filters)

            # Serialize the filtered data
            serializer = BranchMasterSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class BranchMasterUpdateAPIView(APIView):
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
            # Retrieve the BranchMaster instance
            instance = BranchMaster.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = BranchMasterSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'BranchMaster updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update BranchMaster',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except BranchMaster.DoesNotExist:
            return Response({
                'msg': 'BranchMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class BranchMasterSoftDeleteAPIView(APIView):
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
            # Retrieve the BranchMaster instance
            instance = BranchMaster.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'BranchMaster deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except BranchMaster.DoesNotExist:
            return Response({
                'msg': 'BranchMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class BranchMasterPermanentDeleteAPIView(APIView):
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
            # Retrieve the BranchMaster instance
            instance = BranchMaster.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'BranchMaster permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except BranchMaster.DoesNotExist:
            return Response({
                'msg': 'BranchMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        

# Create View for EmployeeType
class EmployeeTypeCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the data from the request
            serializer = EmployeeTypeSerializer(data=request.data)
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                # Return success response with the serialized data
                return Response({
                    'status': 'success',
                    'message': 'EmployeeType created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Failed to create EmployeeType.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating EmployeeType.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
# Retrieve View for EmployeeType
class EmployeeTypeRetrieveAPIView(APIView):
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
            # Retrieve the EmployeeType instance
            instance =EmployeeType.objects.get(pk=effect_type_id)
            serializer = EmployeeTypeSerializer(instance)
            
            response_data = {
                'msg': 'EmployeeType retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except EmployeeType.DoesNotExist:
            return Response({
                'msg': 'EmployeeType not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
# Retrieve All View for EmployeeType
class EmployeeTypeListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract filter value for is_active from request data
            queryset = EmployeeType.objects.filter(flag=True).order_by('-id')
            serializer = EmployeeTypeSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'EmployeeType retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving EmployeeTypes.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)            
# Active EmployeeType List View
class ActiveEmployeeTypeListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Extract filter value for is_active from request data
            queryset = EmployeeType.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = EmployeeTypeSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'EmployeeType retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving EmployeeTypes.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
class EmployeeTypeUpdateAPIView(APIView):
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
            # Retrieve the EmployeeType instance
            instance = EmployeeType.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = EmployeeTypeSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'EmployeeType updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update EmployeeType',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except EmployeeType.DoesNotExist:
            return Response({
                'msg': 'EmployeeType not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EmployeeTypeSoftDeleteAPIView(APIView):
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
            # Retrieve the EmployeeType instance
            instance = EmployeeType.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'EmployeeType deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except EmployeeType.DoesNotExist:
            return Response({
                'msg': 'EmployeeType not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class EmployeeTypePermanentDeleteAPIView(APIView):
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
            # Retrieve the EmployeeType instance
            instance = EmployeeType.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'EmployeeType permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except EmployeeType.DoesNotExist:
            return Response({
                'msg': 'EmployeeType not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)       



# Create View for EmployeeMaster
class EmployeeMasterCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the data from the request
            serializer = EmployeeMasterSerializer(data=request.data)
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                # Return success response with the serialized data
                return Response({
                    'status': 'success',
                    'message': 'EmployeeMaster created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Failed to create EmployeeMaster.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating EmployeeMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# Retrieve View for EmployeeMaster
class EmployeeMasterRetrieveAPIView(APIView):
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
            # Retrieve the EmployeeType instance
            instance =EmployeeMaster.objects.get(pk=effect_type_id)
            serializer = EmployeeMasterSerializer(instance)
            
            response_data = {
                'msg': ' EmployeeMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except EmployeeMaster.DoesNotExist:
            return Response({
                'msg': 'EmployeeMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

# Retrieve All View for EmployeeMaster
class EmployeeMasterListAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract filter value for is_active from request data
            queryset = EmployeeMaster.objects.filter(flag=True).order_by('-id')
            serializer = EmployeeMasterSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'EmployeeMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving EmployeeMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
# Active EmployeeMaster List View
class ActiveEmployeeMasterListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Extract filter value for is_active from request data
            queryset = EmployeeMaster.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = EmployeeMasterSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'EmployeeMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving EmployeeMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeMasterFilterView(APIView): 
    def post(self, request, *args, **kwargs):        
        try:       
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(EmployeeMaster, filters)

            # Serialize the filtered data
            serializer = EmployeeMasterSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class EmployeeMasterUpdateAPIView(APIView):
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
            # Retrieve the EmployeeMaster instance
            instance = EmployeeMaster.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = EmployeeMasterSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'EmployeeMaster updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update EmployeeMaster',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except EmployeeMaster.DoesNotExist:
            return Response({
                'msg': 'EmployeeMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'msg': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EmployeeMasterSoftDeleteAPIView(APIView):
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
            # Retrieve the EmployeeMaster instance
            instance = EmployeeMaster.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'EmployeeMaster deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except EmployeeMaster.DoesNotExist:
            return Response({
                'msg': 'EmployeeMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class EmployeeMasterPermanentDeleteAPIView(APIView):
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
            # Retrieve the EmployeeMaster instance
            instance = EmployeeMaster.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'EmployeeMaster permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except EmployeeMaster.DoesNotExist:
            return Response({
                'msg': 'EmployeeMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

