from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import RouteStations, RouteMaster
from branches.models import BranchMaster

User = get_user_model()

# Serializer for RouteStations
class RouteStationsSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    updated_by = serializers.StringRelatedField()
   
    class Meta:
        model = RouteStations
        fields = [
            'id','route_station', 'km', 
            'created_by', 'created_at', 'updated_by', 'updated_at', 
            'is_active', 'flag'
        ]

# Serializer for RouteMaster
class RouteMasterSerializer(serializers.ModelSerializer):
    route_stations = RouteStationsSerializer(many=True, read_only=True)    

    class Meta:
        model = RouteMaster
        fields = [
            'id', 'route_name','from_branch', 'to_branch', 'route_stations', 
            'created_by', 'created_at', 'updated_by', 
            'updated_at', 'is_active', 'flag'
        ]