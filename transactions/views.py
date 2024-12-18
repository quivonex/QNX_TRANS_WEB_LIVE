from django.shortcuts import render

from transactions.serializers import CollectionTypesSerializer, DeliveryTypesSerializer, LoadTypesSerializer, PaidTypesSerializer, PayTypesSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CollectionTypes, DeliveryTypes, LoadTypes, PaidTypes, PayTypes

# Create your views here.
class LoadTypesCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Add the request object to pass to the model's save method
            serializer = LoadTypesSerializer(data=request.data)

            if serializer.is_valid():
                # Save the instance, passing the request to handle created_by and updated_by
                serializer.save(created_by=request.user)

                return Response(
                    {
                        "message": "Load Type created successfully",
                        "status": status.HTTP_201_CREATED,
                        "data": [serializer.data]
                    },
                    status=status.HTTP_201_CREATED
                )

            # Return validation errors if the data is not valid
            return Response(
                {
                    "message": "Failed to create Load Type",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Handle any unexpected errors during the process
            return Response(
                {
                    "message": "An error occurred while creating Load Type",
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class LoadTypesRetrieveView(APIView):
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
            item = LoadTypes.objects.get(pk=item_id)
        except LoadTypes.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Item not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item data
        serializer = LoadTypesSerializer(item)

        # Return a success response with the item data
        return Response({
            "status": "success",
            "message": "Item retrieved successfully.",
            "data": [serializer.data]
        }, status=status.HTTP_200_OK)
    
class LoadTypesRetrieveAllView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = LoadTypes.objects.filter(flag=True).order_by('-id')

            
            # Serialize the items data
            serializer = LoadTypesSerializer(items, many=True)
            
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
    
class LoadTypesRetrieveActiveView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve only active items from the database
            queryset = LoadTypes.objects.filter(is_active=True,flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = LoadTypesSerializer(queryset, many=True)
            
            # Return a success response with the items data
            response_data = {
                'msg': 'LoadTypes retrieved successfully',
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
    
class LoadTypesUpdateAPIView(APIView):
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
            # Retrieve the LoadTypes instance
            instance = LoadTypes.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = LoadTypesSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'LoadTypes updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update LoadTypes',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except LoadTypes.DoesNotExist:
            return Response({
                'msg': 'LoadTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class LoadTypesSoftDeleteAPIView(APIView):
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
            # Retrieve the LoadTypes instance
            instance = LoadTypes.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'LoadTypes deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except LoadTypes.DoesNotExist:
            return Response({
                'msg': 'LoadTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class LoadTypesPermanentDeleteAPIView(APIView):
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
            # Retrieve the LoadTypes instance
            instance = LoadTypes.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'LoadTypes permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except LoadTypes.DoesNotExist:
            return Response({
                'msg': 'LoadTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class PaidTypesCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Add the request object to pass to the model's save method
            serializer = PaidTypesSerializer(data=request.data)

            if serializer.is_valid():
                # Save the instance, passing the request to handle created_by and updated_by
                serializer.save(created_by=request.user)

                return Response(
                    {
                        "message": "PaidTypes created successfully",
                        "status": "success",
                        "data": [serializer.data]
                    },
                    status=status.HTTP_201_CREATED
                )

            # Return validation errors if the data is not valid
            return Response(
                {
                    "message": "Failed to create Paid Type",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Handle any unexpected errors during the process
            return Response(
                {
                    "message": "An error occurred while creating Load Type",
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
   
class PaidTypesRetrieveView(APIView):
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
            item = PaidTypes.objects.get(pk=item_id)
        except PaidTypes.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Item not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item data
        serializer = PaidTypesSerializer(item)

        # Return a success response with the item data
        return Response({
            "status": "success",
            "message": "Item retrieved successfully.",
            "data": [serializer.data]
        }, status=status.HTTP_200_OK)
    
class PaidTypesRetrieveAllView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = PaidTypes.objects.filter(flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = PaidTypesSerializer(items, many=True)
            
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
    
class PaidTypesRetrieveActiveView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve only active items from the database
            queryset = PaidTypes.objects.filter(is_active=True,flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = PaidTypesSerializer(queryset, many=True)
            
            # Return a success response with the items data
            response_data = {
                'msg': 'PaidTypes retrieved successfully',
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
    
class PaidTypesUpdateAPIView(APIView):
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
            # Retrieve the PaidTypes instance
            instance = PaidTypes.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = PaidTypesSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'PaidTypes updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update PaidTypes',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except PaidTypes.DoesNotExist:
            return Response({
                'msg': 'PaidTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class PaidTypesSoftDeleteAPIView(APIView):
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
            # Retrieve the PaidTypes instance
            instance = PaidTypes.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'PaidTypes deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except PaidTypes.DoesNotExist:
            return Response({
                'msg': 'PaidTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class PaidTypesPermanentDeleteAPIView(APIView):
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
            # Retrieve the PaidTypes instance
            instance = PaidTypes.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'PaidTypes permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except PaidTypes.DoesNotExist:
            return Response({
                'msg': 'PaidTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        

class PayTypesCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Add the request object to pass to the model's save method
            serializer = PayTypesSerializer(data=request.data)

            if serializer.is_valid():
                # Save the instance, passing the request to handle created_by and updated_by
                serializer.save(created_by=request.user)

                return Response(
                    {
                        "message": "PayTypes created successfully",
                        "status": status.HTTP_201_CREATED,
                        "data": [serializer.data]
                    },
                    status=status.HTTP_201_CREATED
                )

            # Return validation errors if the data is not valid
            return Response(
                {
                    "message": "Failed to create PayTypes",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Handle any unexpected errors during the process
            return Response(
                {
                    "message": "An error occurred while creating PayTypes",
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
   
class PayTypesRetrieveView(APIView):
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
            item = PayTypes.objects.get(pk=item_id)
        except PayTypes.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Item not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item data
        serializer = PayTypesSerializer(item)

        # Return a success response with the item data
        return Response({
            "status": "success",
            "message": "Item retrieved successfully.",
            "data": [serializer.data]
        }, status=status.HTTP_200_OK)
    
class PayTypesRetrieveAllView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = PayTypes.objects.filter(flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = PayTypesSerializer(items, many=True)
            
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
    
class PayTypesRetrieveActiveView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve only active items from the database
            queryset = PayTypes.objects.filter(is_active=True,flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = PayTypesSerializer(queryset, many=True)
            
            # Return a success response with the items data
            response_data = {
                'msg': 'PayTypes retrieved successfully',
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
    
class PayTypesUpdateAPIView(APIView):
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
            # Retrieve the PayTypes instance
            instance = PayTypes.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = PayTypesSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'PayTypes updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update PayTypes',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except PayTypes.DoesNotExist:
            return Response({
                'msg': 'PayTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class PayTypesSoftDeleteAPIView(APIView):
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
            # Retrieve the PayTypes instance
            instance = PayTypes.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'PayTypes deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except PayTypes.DoesNotExist:
            return Response({
                'msg': 'PayTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class PayTypesPermanentDeleteAPIView(APIView):
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
            # Retrieve the PayTypes instance
            instance = PayTypes.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'PayTypes permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except PayTypes.DoesNotExist:
            return Response({
                'msg': 'PayTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        

class CollectionTypesCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Add the request object to pass to the model's save method
            serializer = CollectionTypesSerializer(data=request.data)

            if serializer.is_valid():
                # Save the instance, passing the request to handle created_by and updated_by
                serializer.save(created_by=request.user)

                return Response(
                    {
                        "message": "CollectionTypes created successfully",
                        "status": status.HTTP_201_CREATED,
                        "data": [serializer.data]
                    },
                    status=status.HTTP_201_CREATED
                )

            # Return validation errors if the data is not valid
            return Response(
                {
                    "message": "Failed to create PayTypes",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Handle any unexpected errors during the process
            return Response(
                {
                    "message": "An error occurred while creating CollectionTypes",
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
   
class CollectionTypesRetrieveView(APIView):
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
            item = CollectionTypes.objects.get(pk=item_id)
        except CollectionTypes.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Item not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item data
        serializer = CollectionTypesSerializer(item)

        # Return a success response with the item data
        return Response({
            "status": "success",
            "message": "Item retrieved successfully.",
            "data": [serializer.data]
        }, status=status.HTTP_200_OK)
    
class CollectionTypesRetrieveAllView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = CollectionTypes.objects.filter(flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = CollectionTypesSerializer(items, many=True)
            
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
    
class CollectionTypesRetrieveActiveView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve only active items from the database
            queryset = CollectionTypes.objects.filter(is_active=True,flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = CollectionTypesSerializer(queryset, many=True)
            
            # Return a success response with the items data
            response_data = {
                'msg': 'CollectionTypes retrieved successfully',
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

class CollectionTypesRetrieveForBookingMemoView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve only active items from the database
            queryset = CollectionTypes.objects.filter(is_show_booking_memo=True,is_active=True,flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = CollectionTypesSerializer(queryset, many=True)
            
            # Return a success response with the items data
            response_data = {
                'msg': 'CollectionTypes retrieved successfully',
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
 

class CollectionTypesUpdateAPIView(APIView):
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
            # Retrieve the CollectionTypes instance
            instance = CollectionTypes.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = CollectionTypesSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'CollectionTypes updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update CollectionTypes',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except CollectionTypes.DoesNotExist:
            return Response({
                'msg': 'CollectionTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CollectionTypesSoftDeleteAPIView(APIView):
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
            # Retrieve the CollectionTypes instance
            instance = CollectionTypes.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'CollectionTypes deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except CollectionTypes.DoesNotExist:
            return Response({
                'msg': 'CollectionTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class CollectionTypesPermanentDeleteAPIView(APIView):
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
            # Retrieve the CollectionTypes instance
            instance = CollectionTypes.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'CollectionTypes permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except CollectionTypes.DoesNotExist:
            return Response({
                'msg': 'CollectionTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class DeliveryTypesCreateView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Add the request object to pass to the model's save method
            serializer = DeliveryTypesSerializer(data=request.data)

            if serializer.is_valid():
                # Save the instance, passing the request to handle created_by and updated_by
                serializer.save(created_by=request.user)

                return Response(
                    {
                        "message": "DeliveryTypes created successfully",
                        "status": status.HTTP_201_CREATED,
                        "data": [serializer.data]
                    },
                    status=status.HTTP_201_CREATED
                )

            # Return validation errors if the data is not valid
            return Response(
                {
                    "message": "Failed to create DeliveryTypes",
                    "status": status.HTTP_400_BAD_REQUEST,
                    "errors": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            # Handle any unexpected errors during the process
            return Response(
                {
                    "message": "An error occurred while creating DeliveryTypes",
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
   
class DeliveryTypesRetrieveView(APIView):
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
            item = DeliveryTypes.objects.get(pk=item_id)
        except DeliveryTypes.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Item not found.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the item data
        serializer = DeliveryTypesSerializer(item)

        # Return a success response with the item data
        return Response({
            "status": "success",
            "message": "Item retrieved successfully.",
            "data": [serializer.data]
        }, status=status.HTTP_200_OK)
    
class DeliveryTypesRetrieveAllView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all items from the database
            items = DeliveryTypes.objects.filter(flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = DeliveryTypesSerializer(items, many=True)
            
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
    
class DeliveryTypesRetrieveActiveView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve only active items from the database
            queryset = DeliveryTypes.objects.filter(is_active=True,flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = DeliveryTypesSerializer(queryset, many=True)
            
            # Return a success response with the items data
            response_data = {
                'msg': 'DeliveryTypes retrieved successfully',
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
    
class DeliveryTypesRetrieveForBookingMemoView(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            # Retrieve only active items from the database
            queryset = DeliveryTypes.objects.filter(is_show_booking_memo=True,is_active=True,flag=True).order_by('-id')
            
            # Serialize the items data
            serializer = DeliveryTypesSerializer(queryset, many=True)
            
            # Return a success response with the items data
            response_data = {
                'msg': 'DeliveryTypes retrieved successfully',
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
 

class DeliveryTypesUpdateAPIView(APIView):
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
            # Retrieve the DeliveryTypes instance
            instance = DeliveryTypes.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = DeliveryTypesSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'DeliveryTypes updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update DeliveryTypes',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except DeliveryTypes.DoesNotExist:
            return Response({
                'msg': 'DeliveryTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DeliveryTypesSoftDeleteAPIView(APIView):
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
            # Retrieve the DeliveryTypes instance
            instance = DeliveryTypes.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'DeliveryTypes deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except DeliveryTypes.DoesNotExist:
            return Response({
                'msg': 'DeliveryTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class DeliveryTypesPermanentDeleteAPIView(APIView):
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
            # Retrieve the DeliveryTypes instance
            instance = DeliveryTypes.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'DeliveryTypes permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except DeliveryTypes.DoesNotExist:
            return Response({
                'msg': 'DeliveryTypes not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
