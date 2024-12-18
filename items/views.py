from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import ItemDetailsMaster, QuotationTypes
from .serializers import ItemDetailsMasterSerializer, QuotationTypesSerializer
from rest_framework.exceptions import ValidationError
from company.filters import apply_filters


class ItemDetailsMasterCreateView(APIView):
   
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the request data and context
            serializer = ItemDetailsMasterSerializer(data=request.data, context={'request': request})
            
            # Validate the incoming data
            if serializer.is_valid():
                # Save the serializer, which triggers the save method in the model
                serializer.save(created_by=request.user)
                
                # Return a success response with data and a custom message
                return Response({
                    "status": "success",
                    "message": "Item Details created successfully.",
                    "data": [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # If the data is not valid, return an error response
            return Response({
                "status": "error",
                "message": "There was an error creating the item.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while creating the item.",
                "error": str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ItemDetailsMasterRetrieveView(APIView):
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
            item = ItemDetailsMaster.objects.get(pk=item_id)
        except ItemDetailsMaster.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Item not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item data
        serializer = ItemDetailsMasterSerializer(item)

        # Return a success response with the item data
        return Response({
            "status": "success",
            "message": "Item retrieved successfully.",
            "data": [serializer.data]
        }, status=status.HTTP_200_OK)
    
class ItemDetailsMasterRetrieveAllView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = ItemDetailsMaster.objects.filter(flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = ItemDetailsMasterSerializer(items, many=True)
            
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
                "message": "An unexpected error occurred while retrieving items.",
                "error": str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class ItemDetailsMasterRetrieveActiveView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve only active items from the database
            queryset = ItemDetailsMaster.objects.filter(is_active=True,flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = ItemDetailsMasterSerializer(queryset, many=True)
            
            # Return a success response with the items data
            response_data = {
                'msg': 'ItemDetailsMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'msg': 'An unexpected error occurred while retrieving active items.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ItemDetailsMasterFilterView(APIView): 
    def post(self, request, *args, **kwargs):        
        try:       
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(ItemDetailsMaster, filters)

            # Serialize the filtered data
            serializer = ItemDetailsMasterSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)

class ItemDetailsMasterUpdateAPIView(APIView):
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
            # Retrieve the ItemDetailsMaster instance
            instance = ItemDetailsMaster.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = ItemDetailsMasterSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'ItemDetailsMaster updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update ItemDetailsMaster',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ItemDetailsMaster.DoesNotExist:
            return Response({
                'msg': 'ItemDetailsMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ItemDetailsMasterSoftDeleteAPIView(APIView):
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
            # Retrieve the ItemDetailsMaster instance
            instance = ItemDetailsMaster.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'ItemDetailsMaster deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except ItemDetailsMaster.DoesNotExist:
            return Response({
                'msg': 'ItemDetailsMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class ItemDetailsMasterPermanentDeleteAPIView(APIView):
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
            # Retrieve the ItemDetailsMaster instance
            instance = ItemDetailsMaster.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'ItemDetailsMaster permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except ItemDetailsMaster.DoesNotExist:
            return Response({
                'msg': 'ItemDetailsMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
    
        

class QuotationTypesCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the request data and context
            serializer = QuotationTypesSerializer(data=request.data, context={'request': request})
            
            # Validate the incoming data
            if serializer.is_valid():
                # Save the serializer, which triggers the save method in the model
                serializer.save(created_by=request.user)
                
                # Return a success response with data and a custom message
                return Response({
                    "status": "success",
                    "message": "Quotation Type created successfully.",
                    "data": [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # If the data is not valid, return an error response
            return Response({
                "status": "error",
                "msg": "There was an error creating the quotation type.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                "status": "error",
                "message": "An unexpected error occurred while creating the quotation type.",
                "error": str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuotationTypesRetrieveView(APIView):
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
            item = QuotationTypes.objects.get(pk=item_id)
        except QuotationTypes.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Quotation type not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item data
        serializer = QuotationTypesSerializer(item)

        # Return a success response with the item data
        return Response({
            "status": "success",
            "message": "Quotation type retrieved successfully.",
            "data": [serializer.data]
        }, status=status.HTTP_200_OK)
    
class QuotationTypesRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = QuotationTypes.objects.filter(flag=True).order_by('-id')


            # Serialize the items data
            serializer = QuotationTypesSerializer(items, many=True)

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
                "message": "An unexpected error occurred while retrieving the items.",
                "error": str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class QuotationTypesRetrieveActiveView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve active items from the database
            queryset = QuotationTypes.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = QuotationTypesSerializer(queryset, many=True)
            
            # Return a success response with the serialized data
            response_data = {
                'msg': 'QuotationTypes retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An unexpected error occurred while retrieving the active items.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
class QuotationTypesUpdateAPIView(APIView):
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
            # Retrieve the QuotationTypes instance
            instance = QuotationTypes.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = QuotationTypesSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'QuotationTypes updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update QuotationTypes',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except QuotationTypes.DoesNotExist:
            return Response({
                'msg': 'QuotationTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class QuotationTypesSoftDeleteAPIView(APIView):
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
            # Retrieve the QuotationTypes instance
            instance = QuotationTypes.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'QuotationTypes deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except QuotationTypes.DoesNotExist:
            return Response({
                'msg': 'QuotationTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class QuotationTypesPermanentDeleteAPIView(APIView):
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
            # Retrieve the QuotationTypes instance
            instance = QuotationTypes.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'QuotationTypes permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except QuotationTypes.DoesNotExist:
            return Response({
                'msg': 'QuotationTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
