# # routes/views.py
# from django.shortcuts import render
# from .forms import DistanceForm
# import pgeocode


# def calculate_distance_view(request):
#     form = DistanceForm(request.POST or None)
#     distance = None
#     if request.method == 'POST' and form.is_valid():
#         postal_code1 = form.cleaned_data['postal_code1']
#         postal_code2 = form.cleaned_data['postal_code2']
#         dist = pgeocode.GeoDistance('IN')  # Assuming 'IN' for India
#         distance = dist.query_postal_code(postal_code1, postal_code2)
#     context = {
#         'form': form,
#         'distance': distance
#     }
#     return render(request, 'calculate_distance.html', context)


from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import RouteMaster, RouteStations
from .serializers import RouteMasterSerializer, RouteStationsSerializer
from branches.models import BranchMaster
from django.db import transaction
from vehicals.models import VehicalMaster,DriverMaster
from vehicals.serializers import VehicalMasterSerializer,DriverMasterSerializer
from collection.models import BookingMemo, TripBokkingMemos,TripMemo
from collection.serializers import BookingMemoSerializer, TripMemoSerializer
from branches.serializers import BranchMasterSerializer
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from company.filters import apply_filters


class RouteMasterCreateView(APIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Deserialize RouteMaster data
        route_master_serializer = RouteMasterSerializer(data=request.data)
        if route_master_serializer.is_valid():
            # Create the RouteMaster instance but don't save it yet
            route_master_instance = route_master_serializer.create(
                validated_data=route_master_serializer.validated_data
            )
            
            # Get the 'route_stations' from the request
            route_stations_data = request.data.get('route_stations', [])

            route_stations_to_add = []

            if route_stations_data:
                try:
                    for item in route_stations_data:
                        new_station = RouteStations.objects.create(                            
                            route_station=BranchMaster.objects.get(pk=item['route_station']) if item.get('route_station') else None,
                            km=item.get('km', 0),
                            created_by=request.user,
                        )
                        route_stations_to_add.append(new_station)
                except BranchMaster.DoesNotExist:
                    return Response({"error": "BranchMaster not found"}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({
                        'msg': 'An error occurred',
                        'status': 'error',
                        'error': str(e)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Attach the RouteStations to the RouteMaster instance
            route_master_instance.route_stations.set(route_stations_to_add)

            # Save the main RouteMaster object
            route_master_instance.save()

            # Return the serialized response of the newly created RouteMaster object
            response_serializer = RouteMasterSerializer(route_master_instance)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(route_master_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RouteMasterRetrieveView(APIView):
    def post(self, request, *args, **kwargs):
        route_master_id = request.data.get('id')

        if not route_master_id:
            return Response({
                'message': 'RouteMaster id is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            route_master_instance = RouteMaster.objects.get(id=route_master_id)
        except RouteMaster.DoesNotExist:
            return Response({
                'message': 'RouteMaster not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the retrieved instance
        serializer = RouteMasterSerializer(route_master_instance)
        return Response({
            'message': 'RouteMaster retrieved successfully',
            'status': 'success',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

class RouteMasterRetrieveActiveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            branch_id = request.data.get("branch_id")
            if not branch_id:
                return Response({
                    "status": "error",
                    "message": "Branch ID is required."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            route_masters = RouteMaster.objects.filter(is_active=True,flag=True,route_stations__route_station_id=branch_id).order_by('-id')

            # Serialize all RouteMaster instances
            serializer = RouteMasterSerializer(route_masters, many=True)

            return Response({
                'message': 'RouteMaster retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'message': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RouteMasterRetrieveActiveListAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            
            route_masters = RouteMaster.objects.filter(is_active=True,flag=True).order_by('-id')

            # Serialize all RouteMaster instances
            serializer = RouteMasterSerializer(route_masters, many=True)

            return Response({
                'message': 'RouteMaster retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'message': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RouteMasterRetrieveForBookingMemoView(APIView):
    def post(self, request, *args, **kwargs):
        route_master_id = request.data.get('id')
        if not route_master_id:
            return Response({
                'message': 'RouteMaster id is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        branch_id = request.data.get("branch_id")
        if not branch_id:
            return Response({
                "status": "error",
                "message": "Branch ID is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            route_master_instance = RouteMaster.objects.get(id=route_master_id)        
            from_branches = {
                station.route_station for station in route_master_instance.route_stations.all()                
            }
            filtered_branches = [branch for branch in from_branches if branch.id == branch_id]            
            branch_serializer = BranchMasterSerializer(filtered_branches, many=True)

            response_data = {
                'msg': 'branches retrieved successfully',
                'status': 'success',
                'data': [branch_serializer.data]
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving data.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ToBranchListByRouteAndFromBranchView(APIView):
    def post(self, request, *args, **kwargs):        
        route_id = request.data.get('route_id')
        
        if not route_id:
            return Response({
                'message': 'route_id are required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the RouteMaster instance by route_id
            route_master_instance = RouteMaster.objects.get(id=route_id)

            # Filter RouteStations related to the RouteMaster with the specified from_branch_id
            to_branches = {
                station.route_station for station in route_master_instance.route_stations.all()                
            }

            # Serialize the unique to_branches
            to_branch_serializer = BranchMasterSerializer(to_branches, many=True)            
            response_data = {
                'msg': 'ToBranch list retrieved successfully',
                'status': 'success',
                'data': to_branch_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except RouteMaster.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'RouteMaster with the given ID does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving data.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class kmByRouteAndFromBranchandToBranchView(APIView):
    def post(self, request, *args, **kwargs):        
        route_id = request.data.get('route_id')       
        to_branch_id = request.data.get('to_branch_id')

        if not route_id or not to_branch_id:
            return Response({
                'message': 'Both route_id and to_branch_id are required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the RouteMaster instance by route_id
            route_master_instance = RouteMaster.objects.get(id=route_id)

            # Filter RouteStations related to the RouteMaster with the specified from_branch_id
            station = {
                station for station in route_master_instance.route_stations.all()
                if station.route_station_id == to_branch_id
            }

            km = []
            for st in station :
                nkm = st.km
                km.append(nkm)

            # Serialize the unique to_branches
            station_serializers = RouteStationsSerializer(station, many=True)            
            response_data = {
                'msg': 'Kilometer list retrieved successfully',
                'status': 'success',
                'data': km
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except RouteMaster.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'RouteMaster with the given ID does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An error occurred while retrieving data.',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# For last booking memo with this vehical and route and his trip memo match with this vehical open trip memo
# means have the last_bookingmemo's route is same as the requested route
class TripNumberRetrieveView(APIView):    
    def post(self, request, *args, **kwargs):
        try:
            # Extract route_id and vehicle_id from request
            route_id = request.data.get('route_id')
            vehicle_id = request.data.get('vehical_id')

            # Validate required fields
            if not route_id or not vehicle_id:
                return Response({
                    "status": "error",
                    "msg": "Both route_id and vehicle_id are required.",
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

            # Check if the vehicle is not available
            if vehicle.is_available:
                return Response({
                    "status": "success",
                    "msg": f"The vehicle with number {vehicle.vehical_number} is available.",
                    "data": 0
                }, status=status.HTTP_200_OK)

            # Fetch the first open TripMemo for this vehicle
            vehicle_trip_memo = TripMemo.objects.filter(
                vehicle_no=vehicle,
                trip_mode='OPEN',
                is_active=True,
                flag=True
            ).first()
            print(vehicle_trip_memo)
            if not vehicle_trip_memo:
                return Response({
                    "status": "error",
                    "msg": "No active TripMemo found for the vehicle.",
                    "data": 0
                }, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the BookingMemo matching route_id and vehicle_id
            booking_memo_queryset = BookingMemo.objects.filter(
                vehicle_trip_route=route_id,
                vehical_no=vehicle_id,
                is_active=True,
                flag=True
            ).exclude(
                trip_no__in=['0', 0, None, '']
            ).filter(
                trip_no__regex=r'^\d{10}$'
            ).order_by('-id')

            booking_memo = booking_memo_queryset.first()
            print(booking_memo)
            if not booking_memo:
                return Response({
                    "status": "error",
                    "msg": "No valid BookingMemo found for the provided route and vehicle.",
                    "data": 0
                }, status=status.HTTP_404_NOT_FOUND)

            # Fetch the TripMemo associated with the BookingMemo
            booking_trip_memo = TripMemo.objects.filter(
                booking_memos__booking_memo=booking_memo,
                is_active=True,
                flag=True,
                trip_mode='OPEN'
            ).first()

            # Check if both TripMemo objects match
            if vehicle_trip_memo and booking_trip_memo and vehicle_trip_memo.id == booking_trip_memo.id:
                serializer = TripMemoSerializer(vehicle_trip_memo)
                return Response({
                    "status": "success",
                    "msg": f"The vehicle with number {vehicle.vehical_number} is currently on Trip {vehicle_trip_memo.trip_no}, traveling from {vehicle_trip_memo.from_branch.branch_name} to {vehicle_trip_memo.to_branch.branch_name}.",
                    "data": [serializer.data]
                }, status=status.HTTP_200_OK)

            return Response({
                "status": "error",
                "msg": "No matching TripMemo found for the vehicle and booking.",
                "data": 0
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": "error",
                "msg": "An unexpected error occurred.",
                "data": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# For this vehical open trip memo's any booking memo's route is match route
# means inside this open trip any booking have same requested route
class TripNumberRetrieveView1(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract route_id and vehicle_id from request
            route_id = request.data.get('route_id')
            vehicle_id = request.data.get('vehical_id')

            # Validate required fields
            if not route_id or not vehicle_id:
                return Response({
                    "status": "error",
                    "msg": "Both route_id and vehicle_id are required.",
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

            # Check if the vehicle is available
            if vehicle.is_available:
                return Response({
                    "status": "success",
                    "msg": f"The vehicle with number {vehicle.vehical_number} is available.",
                    "data": 0
                }, status=status.HTTP_200_OK)

            # Fetch the first open TripMemo for this vehicle
            vehicle_trip_memo = TripMemo.objects.filter(
                vehicle_no=vehicle,
                trip_mode='OPEN',
                is_active=True,
                flag=True
            ).first()

            if not vehicle_trip_memo:
                return Response({
                    "status": "error",
                    "msg": "No active TripMemo found for the vehicle.",
                    "data": 0
                }, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve associated BookingMemo objects through TripBookingMemos
            booking_memos = BookingMemo.objects.filter(
                id__in=TripBokkingMemos.objects.filter(
                    tripmemo=vehicle_trip_memo,
                    is_active=True,
                    flag=True
                ).values_list('booking_memo_id', flat=True),
                is_active=True,
                flag=True
            )

            if not booking_memos.exists():
                return Response({
                    "status": "error",
                    "msg": "No associated BookingMemos found for the TripMemo.",
                    "data": 0
                }, status=status.HTTP_404_NOT_FOUND)

            # Check if any BookingMemo's vehicle_trip_route matches the current route
            matching_booking_memo = booking_memos.filter(vehicle_trip_route=route_id).first()

            if matching_booking_memo:
                serializer = TripMemoSerializer(vehicle_trip_memo)
                return Response({
                    "status": "success",
                    "msg": f"The vehicle with number {vehicle.vehical_number} is currently on Trip {vehicle_trip_memo.trip_no}, traveling from {vehicle_trip_memo.from_branch.branch_name} to {vehicle_trip_memo.to_branch.branch_name}.",
                    "data": [serializer.data]
                }, status=status.HTTP_200_OK)

            # If no matching BookingMemo is found
            return Response({
                "status": "error",
                "msg": "No BookingMemo matches the current route for the TripMemo.",
                "data": 0
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": "error",
                "msg": "An unexpected error occurred.",
                "data": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# For this vehical open trip memo's any booking memo's any route's is have the From_branch and to_branch
# means inside this open trip any booking's any route have requested from and to branch
class TripNumberRetrieveView2(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract route_id, vehicle_id, from_branch_id, and to_branch_id from request
            route_id = request.data.get('route_id')
            vehicle_id = request.data.get('vehicle_id')
            from_branch_id = request.data.get('from_branch_id')
            to_branch_id = request.data.get('to_branch_id')

            # Validate required fields
            if not route_id or not vehicle_id or not from_branch_id or not to_branch_id:
                return Response({
                    "status": "error",
                    "msg": "route_id, vehicle_id, from_branch_id, and to_branch_id are all required.",
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

            # Check if the vehicle is available
            if vehicle.is_available:
                return Response({
                    "status": "success",
                    "msg": f"The vehicle with number {vehicle.vehical_number} is available.",
                    "data": 0
                }, status=status.HTTP_200_OK)

            # Fetch the first open TripMemo for this vehicle
            vehicle_trip_memo = TripMemo.objects.filter(
                vehicle_no=vehicle,
                trip_mode='OPEN',
                is_active=True,
                flag=True
            ).first()

            if not vehicle_trip_memo:
                return Response({
                    "status": "error",
                    "msg": "No active TripMemo found for the vehicle.",
                    "data": 0
                }, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve associated BookingMemo objects through TripBookingMemos
            booking_memos = BookingMemo.objects.filter(
                id__in=TripBokkingMemos.objects.filter(
                    tripmemo=vehicle_trip_memo,
                    is_active=True,
                    flag=True
                ).values_list('booking_memo_id', flat=True),
                is_active=True,
                flag=True
            )

            if not booking_memos.exists():
                return Response({
                    "status": "error",
                    "msg": "No associated BookingMemos found for the TripMemo.",
                    "data": 0
                }, status=status.HTTP_404_NOT_FOUND)

            # Check if from_branch_id and to_branch_id are present in any vehicle_trip_route
            matching_routes = booking_memos.filter(
                Q(vehicle_trip_route__route_stations__route_station__id=from_branch_id) |
                Q(vehicle_trip_route__route_stations__route_station__id=to_branch_id)
            ).distinct()

            # Ensure both from_branch_id and to_branch_id are present
            has_from_branch = matching_routes.filter(
                vehicle_trip_route__route_stations__route_station__id=from_branch_id
            ).exists()
            has_to_branch = matching_routes.filter(
                vehicle_trip_route__route_stations__route_station__id=to_branch_id
            ).exists()

            if has_from_branch and has_to_branch:
                serializer = TripMemoSerializer(vehicle_trip_memo)
                return Response({
                    "status": "success",
                    "msg": f"The vehicle with number {vehicle.vehical_number} is currently on Trip {vehicle_trip_memo.trip_no}, traveling from {vehicle_trip_memo.from_branch.branch_name} to {vehicle_trip_memo.to_branch.branch_name}.",
                    "data": [serializer.data]
                }, status=status.HTTP_200_OK)

            return Response({
                "status": "error",
                "msg": "The requested branches are not present in the vehicle's route.",
                "data": 0
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": "error",
                "msg": "An unexpected error occurred.",
                "data": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RouteMasterRetrieveAllView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            route_masters = RouteMaster.objects.filter(flag=True).order_by('-id')

            # Serialize all RouteMaster instances
            serializer = RouteMasterSerializer(route_masters, many=True)

            return Response({
                'message': 'RouteMaster retrieved successfully',
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'message': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RouteMasterFilterView(APIView): 
    def post(self, request, *args, **kwargs):        
        try:       
            # Extract filters from the request body
            filters = request.data.get("filters", {})
            if not isinstance(filters, dict):
                raise ValidationError("Filters must be a dictionary.")

            # Apply dynamic filters
            queryset = apply_filters(RouteMaster, filters)

            # Serialize the filtered data
            serializer = RouteMasterSerializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=200)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=400)        

class RouteMasterUpdateAPIView(APIView):    
    @transaction.atomic
    def post(self, request, *args, **kwargs):        
        route_master_id = request.data.get('id')     
        if not route_master_id:
            return Response({
                'message': 'RouteMaster id is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)       
        try:
            route_master_instance = RouteMaster.objects.get(id=route_master_id)

            # Initialize serializer with instance and updated data
            serializer = RouteMasterSerializer(route_master_instance, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save(updated_by=request.user)              
                # Handle RouteStations update logic
                route_stations_data = request.data.get('route_stations', None)
                if route_stations_data is not None:
                    existing_stations = list(route_master_instance.route_stations.all())                  
                    # Remove stations if empty data
                    if not route_stations_data:
                        for station in existing_stations:
                            station.delete()
                        route_master_instance.route_stations.clear()
                    else:
                        new_station_ids = {item.get('id') for item in route_stations_data if item.get('id') != 0}
                        stations_to_delete = [station for station in existing_stations if station.id not in new_station_ids]

                        for station in stations_to_delete:
                            station.delete()                        
                        stations_to_add = []
                        for item in route_stations_data:                            
                            if item.get('id') == 0:  # New station
                                new_station = RouteStations.objects.create(
                                    route_station=BranchMaster.objects.get(pk=item['route_station']) if item.get('route_station') else None,
                                    km=item.get('km', 0),
                                    created_by=request.user,
                                )
                                stations_to_add.append(new_station)
                            else:                               
                                existing_station = RouteStations.objects.get(pk=item['id'])                               
                                existing_station.route_station = BranchMaster.objects.get(pk=item['route_station']) if item.get('route_station') else None
                                
                                existing_station.km = item.get('km', 0)                           
                                existing_station.save()                                
                        route_master_instance.route_stations.set(stations_to_add + list(existing_stations))

                return Response({
                    'message': 'RouteMaster updated successfully',
                    'status': 'success',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)

            return Response({
                'message': 'Failed to update RouteMaster',
                'status': 'error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except RouteMaster.DoesNotExist:
            return Response({
                'message': 'RouteMaster not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RouteMasterSoftDeleteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        route_master_id = request.data.get('id')

        if not route_master_id:
            return Response({
                'message': 'RouteMaster id is required',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            route_master_instance = RouteMaster.objects.get(id=route_master_id)

            # Set flag to False to soft delete
            route_master_instance.flag = False
            route_master_instance.save()

            return Response({
                'message': 'RouteMaster soft deleted successfully',
                'status': 'success'
            }, status=status.HTTP_200_OK)

        except RouteMaster.DoesNotExist:
            return Response({
                'message': 'RouteMaster not found',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'message': 'An error occurred',
                'status': 'error',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)