from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CompanyMaster, FinancialYears, StateMaster, RegionMaster
from .serializers import CompanyMasterSerializer, FinancialYearsSerializer, StateMasterSerializer, RegionMasterSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated

import os
from django.core.mail import EmailMessage
from django.conf import settings

class FirstActiveCompanyMasterAPIView(APIView):
    permission_classes = [
        AllowAny]

    def post(self, request, *args, **kwargs):
        company = CompanyMaster.objects.filter(is_active=True).first()
        if not company:
            return Response({
                'status': 'error',
                'msg': 'No active company found.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = CompanyMasterSerializer(
            company, context={'request': request})
        return Response({
            'status': 'success',
            'msg': 'First active company retrieved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

class ActiveFinancialYearsListAPIView(APIView):
    permission_classes = [
        AllowAny]
    def post(self, request, *args, **kwargs):
        # Filter queryset to include only active branches
        queryset = FinancialYears.objects.filter(is_active=True,flag=True).order_by('-id')

        # Serialize the filtered queryset
        serializer = FinancialYearsSerializer(queryset, many=True)

        # Return the serialized data
        return Response(serializer.data)

class CompanyMasterView(APIView):
    
    def post(self, request):
        # Check if there's an existing CompanyMaster record
        company_master = CompanyMaster.objects.first()

        if company_master:
            # If a record exists, update it
            serializer = CompanyMasterSerializer(
                company_master, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # If no record exists, create a new one
            serializer = CompanyMasterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Create View for CompanyMaster
class CompanyMasterCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the data from the request
            serializer = CompanyMasterSerializer(data=request.data)
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                # Return success response with the serialized data
                return Response({
                    'status': 'success',
                    'message': 'CompanyMaster created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Failed to create CompanyMaster.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating CompanyMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)     
# Retrieve View for CompanyMaster
class CompanyMasterRetrieveAPIView(APIView):
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
            # Retrieve the CompanyMaster instance
            instance = CompanyMaster.objects.get(pk=effect_type_id)
            serializer = CompanyMasterSerializer(instance)
            
            response_data = {
                'msg': 'CompanyMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except CompanyMaster.DoesNotExist:
            return Response({
                'msg': 'CompanyMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)        
# Retrieve All View for CompanyMaster
class CompanyMasterListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of CompanyMaster
            instances = CompanyMaster.objects.filter(flag=True).order_by('-id')

            serializer = CompanyMasterSerializer(instances, many=True)
            
            response_data = {
                'msg': 'CompanyMaster retrieved successfully',
                'status': 'success',
                'data':[serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving CompanyMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
              
class ActiveCompanyMasterListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Extract filter value for is_active
            queryset = CompanyMaster.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = CompanyMasterSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'CompanyMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving CompanyMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class CompanyMasterUpdateAPIView(APIView):
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
            # Retrieve the CompanyMaster instance
            instance = CompanyMaster.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = CompanyMasterSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'CompanyMaster updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update CompanyMaster',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except CompanyMaster.DoesNotExist:
            return Response({
                'msg': 'CompanyMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CompanyMasterSoftDeleteAPIView(APIView):
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
            # Retrieve the CompanyMaster instance
            instance = CompanyMaster.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'CompanyMaster deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except CompanyMaster.DoesNotExist:
            return Response({
                'msg': 'CompanyMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class CompanyMasterPermanentDeleteAPIView(APIView):
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
            # Retrieve the CompanyMaster instance
            instance = CompanyMaster.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'CompanyMaster permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except CompanyMaster.DoesNotExist:
            return Response({
                'msg': 'CompanyMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
       

    
    
# Repeat similar classes for FinancialYears, StateMaster, RegionMaster

class FinancialYearsCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the data from the request
            serializer = FinancialYearsSerializer(data=request.data)
            
            # Check if the data is valid
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                # Return success response with the serialized data
                return Response({
                    'status': 'success',
                    'message': 'FinancialYears created successfully.',
                    'data': [serializer.data]
                }, status=status.HTTP_201_CREATED)
            
            # Return error response with validation errors
            return Response({
                'status': 'error',
                'message': 'Failed to create FinancialYears.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while creating FinancialYears.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class FinancialYearsRetrieveAPIView(APIView):
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
            # Retrieve the FinancialYears instance
            instance = FinancialYears.objects.get(pk=payment_type_id)
            serializer =  FinancialYearsSerializer(instance)
            
            response_data = {
                'msg': ' FinancialYears retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except  FinancialYears.DoesNotExist:
            return Response({
                'msg': ' FinancialYears not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class FinancialYearsListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of FinancialYears
            instances = FinancialYears.objects.filter(flag=True).order_by('-id')

            serializer = FinancialYearsSerializer(instances, many=True)
            
            response_data = {
                'msg': 'FinancialYears retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving FinancialYears.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# class ActiveFinancialYearsListAPIView(APIView):

#     def post(self, request, *args, **kwargs):
#         try:
#             # Extract filter value for is_active from request data
#             queryset = FinancialYears.objects.filter(is_active=True)
#             serializer = FinancialYearsSerializer(queryset, many=True)
            
#             response_data = {
#                 'msg': 'FinancialYears retrieved successfully',
#                 'status': 'success',
#                 'data': [serializer.data]
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
        
#         except Exception as e:
#             # Handle any unexpected exceptions
#             return Response({
#                 'status': 'error',
#                 'message': 'An error occurred while retrieving FinancialYears.',
#                 'error': str(e)  # Include the error message for debugging
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class FinancialYearsUpdateAPIView(APIView):
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
            # Retrieve the FinancialYears instance
            instance = FinancialYears.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = FinancialYearsSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'FinancialYears updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update FinancialYears',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except FinancialYears.DoesNotExist:
            return Response({
                'msg': 'FinancialYears not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
class FinancialYearsSoftDeleteAPIView(APIView):
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
            # Retrieve the FinancialYears instance
            instance = FinancialYears.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'FinancialYears deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except FinancialYears.DoesNotExist:
            return Response({
                'msg': 'FinancialYears not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class FinancialYearsPermanentDeleteAPIView(APIView):
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
            # Retrieve the FinancialYears instance
            instance = FinancialYears.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'FinancialYears permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except FinancialYears.DoesNotExist:
            return Response({
                'msg': 'FinancialYears not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class StateMasterCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the request data
            serializer = StateMasterSerializer(data=request.data)
            
            # Validate the serializer
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                
                # Create a custom response
                response_data = {
                    'msg': 'StateMaster created successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            
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
                'message': 'An error occurred while creating StateMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class StateMasterRetrieveAPIView(APIView):
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
            # Retrieve the StateMaster instance
            instance = StateMaster.objects.get(pk=receipt_type_id)
            serializer = StateMasterSerializer(instance)
            
            response_data = {
                'msg': 'StateMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except StateMaster.DoesNotExist:
            return Response({
                'msg': 'StateMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class StateMasterListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of StateMaster
            instances = StateMaster.objects.filter(flag=True).order_by('-id')

            serializer = StateMasterSerializer(instances, many=True)
            
            response_data = {
                'msg': 'StateMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving StateMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
class ActiveStateMasterListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Extract filter value for is_active
            queryset = StateMaster.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = StateMasterSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'StateMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving StateMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
class StateMasterUpdateAPIView(APIView):
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
            instance = StateMaster.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = StateMasterSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'StateMaster updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update StateMaster',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except StateMaster.DoesNotExist:
            return Response({
                'msg': 'StateMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class StateMasterSoftDeleteAPIView(APIView):
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
            # Retrieve the StateMaster instance
            instance = StateMaster.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'StateMaster deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except StateMaster.DoesNotExist:
            return Response({
                'msg': 'StateMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class StateMasterPermanentDeleteAPIView(APIView):
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
            # Retrieve the StateMaster instance
            instance = StateMaster.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'StateMaster permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except StateMaster.DoesNotExist:
            return Response({
                'msg': 'StateMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
       

    
class RegionMasterCreateAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Initialize the serializer with the request data
            serializer = RegionMasterSerializer(data=request.data)
            
            # Validate the serializer
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                
                # Create a custom response
                response_data = {
                    'msg': 'RegionMaster created successfully',
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
                'message': 'An error occurred while creating RegionMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
class RegionMasterRetrieveAPIView(APIView):
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
            # Retrieve the RegionMasterinstance
            instance = RegionMaster.objects.get(pk=receipt_type_id)
            serializer = RegionMasterSerializer(instance)
            
            response_data = {
                'msg': 'Receipt type retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except RegionMaster.DoesNotExist:
            return Response({
                'msg': 'RegionMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

class RegionMasterListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all instances of RegionMaster
            instances = RegionMaster.objects.filter(flag=True).order_by('-id')

            serializer = RegionMasterSerializer(instances, many=True)
            
            response_data = {
                'msg': 'RegionMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving RegionMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ActiveRegionMasterListAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            # Retrieve all active instances of RegionMaster
            queryset = RegionMaster.objects.filter(is_active=True,flag=True).order_by('-id')
            serializer = RegionMasterSerializer(queryset, many=True)
            
            response_data = {
                'msg': 'RegionMaster retrieved successfully',
                'status': 'success',
                'data': [serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle any unexpected exceptions
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving RegionMaster.',
                'error': str(e)  # Include the error message for debugging
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RegionMasterUpdateAPIView(APIView):
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
            # Retrieve the RegionMaster instance
            instance = RegionMaster.objects.get(pk=driver_master_id)
            
            # Initialize serializer with the instance and updated data
            serializer = RegionMasterSerializer(instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save(updated_by=request.user)
                return Response({
                    'msg': 'RegionMaster updated successfully',
                    'status': 'success',
                    'data': [serializer.data]
                }, status=status.HTTP_200_OK)
            
            return Response({
                'msg': 'Failed to update RegionMaster',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except RegionMaster.DoesNotExist:
            return Response({
                'msg': 'RegionMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
                return Response({
                    'msg': 'An error occurred',
                    'status': 'error',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RegionMasterSoftDeleteAPIView(APIView):
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
            # Retrieve the RegionMaster instance
            instance = RegionMaster.objects.get(pk=driver_master_id)
            
            # Set is_active to False to soft delete
            instance.flag = False
            instance.save()
            
            return Response({
                'msg': 'RegionMaster deactivated (soft deleted) successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except RegionMaster.DoesNotExist:
            return Response({
                'msg': 'RegionMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
class RegionMasterPermanentDeleteAPIView(APIView):
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
            # Retrieve the RegionMaster instance
            instance = RegionMaster.objects.get(pk=receipt_type_id)
            
            # Permanently delete the instance
            instance.delete()
            
            return Response({
                'msg': 'RegionMaster permanently deleted successfully',
                'status': 'success',
                'data': {}
            }, status=status.HTTP_200_OK)
        
        except RegionMaster.DoesNotExist:
            return Response({
                'msg': 'RegionMaster not found',
                'status': 'error',
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)


def send_email_with_attachment(subject, message, recipient_list, attachment_path=None):
    try:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=recipient_list,
        )
        if attachment_path and os.path.exists(attachment_path):
            email.attach_file(attachment_path)
        email.send()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise
