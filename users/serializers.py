from django.contrib.auth.models import User
from rest_framework import serializers
from branches.models import BranchMaster
from .models import UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from branches.models import BranchMaster
from django.contrib.auth.password_validation import validate_password

class BranchMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchMaster
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    branches = serializers.PrimaryKeyRelatedField(
        queryset=BranchMaster.objects.all(), many=True)
    role = serializers.CharField()

    class Meta:
        model = UserProfile
        fields = ('user', 'branches', 'role','is_active','first_name','last_name')


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        branches = BranchMaster.objects.filter(user_profiles__user=user,is_active=True,flag=True)
        serialized_branches = BranchMasterSerializer(branches, many=True)
        data['branches'] = serialized_branches.data

        return data


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "The two passwords do not match."})

        # You can add custom password validation rules here, or use Django's default ones.
        validate_password(data['new_password'])

        return data


class UserProfileCreateSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    branches = serializers.PrimaryKeyRelatedField(
        queryset=BranchMaster.objects.all(), many=True
    )

    class Meta:
        model = UserProfile
        fields = ('user', 'branches', 'role','first_name','last_name')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        branches_data = validated_data.pop('branches')
        role = validated_data.pop('role')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')

        user = User.objects.create_user(**user_data)
        user_profile = UserProfile.objects.create(user=user, role=role,first_name=first_name,last_name=last_name)
        user_profile.branches.set(branches_data)  

        return user_profile
