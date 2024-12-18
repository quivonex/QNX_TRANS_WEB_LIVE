from django.http import JsonResponse
from branches.models import BranchMaster
from rest_framework.exceptions import ValidationError
from company.filters import apply_filters


def get_branch_pincode(request, branch_id):
    try:
        branch = BranchMaster.objects.get(id=branch_id)
        latitude = branch.latitude
        longitude = branch.longitude
        return JsonResponse({'latitude': latitude, 'longitude': longitude})
    except BranchMaster.DoesNotExist:
        return JsonResponse({'error': 'Branch not found'}, status=404)


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DestinationMaster
from .serializers import DestinationSerializer


class DestinationMasterCreateView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the request data
            serializer = DestinationSerializer(data=request.data, context={'request': request})
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response({
                    'status': 'success',
                    'message': 'Destination created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Invalid data.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating the destination.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DestinationMasterRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        # Extract 'id' from request data to identify the record to retrieve
        item_id = request.data.get('id')

        if item_id is None:
            return Response({
                "status": "error",
                "message": "No ID provided.",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the item details from the database
            item = DestinationMaster.objects.get(pk=item_id)
        except DestinationMaster.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Item not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item data
        serializer = DestinationSerializer(item)

        # Return a success response with the item data
        return Response({
            "status": "success",
            "message": "Item retrieved successfully.",
            "data": [serializer.data]
        }, status=status.HTTP_200_OK)
    
class DestinationMasterRetrieveAllView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = DestinationMaster.objects.filter(flag=True).order_by('-id')

            # Serialize the items data
            serializer = DestinationSerializer(items, many=True)

            # Return a success response with the items data
            return Response({
                "status": "success",
                "message": "Items retrieved successfully.",
                "data": [serializer.data]
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                "status": "error",
                "message": "An error occurred while retrieving the items.",
                "error": str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class DestinationMasterRetrieveActiveView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve active items from the database
            queryset = DestinationMaster.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = DestinationSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'DestinationMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'msg': 'An error occurred while retrieving the items',
                'status': 'error',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DestinationMasterRetrieveOnBranchView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Extract branch_id from request data
            branch_id = request.data.get('branch_id')
            
            if not branch_id:
                return Response({
                    'msg': 'branch_id is required',
                    'status': 'error',
                }, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve destinations filtered by branch_id, is_active, and flag
            queryset = DestinationMaster.objects.filter(branch_id=branch_id, is_active=True, flag=True).order_by('-id')
            
            # Serialize the filtered queryset
            serializer = DestinationSerializer(queryset, many=True)

            # Prepare response data
            response_data = {
                'msg': 'DestinationMaster retrieved successfully for the given branch',
                'status': 'success',
                'data': [serializer.data]  
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'msg': 'An error occurred while retrieving the destinations',
                'status': 'error',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class DestinationMasterFilterView(APIView): 
    def post(self, request, *args, **kwargs):        
        try:       
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(DestinationMaster, filters)

            # Serialize the filtered data
            serializer = DestinationSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)
        
class DestinationMasterUpdateAPIView(APIView):
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
            instance = DestinationMaster.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = DestinationSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'DestinationMaster updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update DestinationMaster',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except DestinationMaster.DoesNotExist:
            return Response({
                'msg': 'DestinationMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DestinationMasterSoftDeleteAPIView(APIView):
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
            # Retrieve the DestinationMaster instance
            instance = DestinationMaster.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'DestinationMaster deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except DestinationMaster.DoesNotExist:
            return Response({
                'msg': 'ReceiptTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class DestinationMasterPermanentDeleteAPIView(APIView):
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
            # Retrieve the DestinationMaster instance
            instance = DestinationMaster.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'DestinationMaster permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except DestinationMaster.DoesNotExist:
            return Response({
                'msg': 'DestinationMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
  