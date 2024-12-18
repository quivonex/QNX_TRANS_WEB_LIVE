from rest_framework import serializers
from .models import DestinationMaster
from branches.models import BranchMaster

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchMaster
        fields = '__all__'

class DestinationSerializer(serializers.ModelSerializer):
    # branch = BranchSerializer()
    class Meta:
        model = DestinationMaster
        fields = '__all__'


    
