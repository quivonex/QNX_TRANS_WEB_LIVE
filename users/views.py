# from django.urls import reverse
# from django.contrib.auth import login as auth_login
# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login
# from django.contrib.auth.forms import AuthenticationForm

# from company.models import FinancialYears
# from .forms import CustomLoginForm
# from django.contrib.auth.decorators import login_required

# import logging

# logger = logging.getLogger(__name__)


# def custom_login_view(request):
#     if request.method == 'POST':
#         form = CustomLoginForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             financial_year = form.cleaned_data.get('financial_year')
#             login(request, user)
#             request.session['financial_year_id'] = financial_year.id
#             logger.debug(f'Financial Year ID set in session: {
#                          financial_year.id}')
#             return redirect('admin:index')  # Adjust this redirect as needed
#     else:
#         form = CustomLoginForm()
#     return render(request, 'registration/login.html', {'form': form})


# @login_required
# def home_view(request):
#     financial_year_id = request.session.get('financial_year_id')
#     print(f'Session Financial Year ID: {
#           financial_year_id}')  # Debugging output

#     if financial_year_id:
#         try:
#             financial_year = FinancialYears.objects.get(id=financial_year_id)
#             # Debugging output
#             print(f'Financial Year: {financial_year.year_name}')
#         except FinancialYears.DoesNotExist:
#             financial_year = None
#             # Debugging output
#             print(f'Financial Year with ID {
#                   financial_year_id} does not exist.')
#     else:
#         financial_year = None
#         print('No Financial Year ID in session.')  # Debugging output

#     context = {
#         'financial_year': financial_year,
#     }
#     return render(request, 'home.html', context)


# def redirect_admin_login(request):
#     return redirect(reverse('login'))

from rest_framework import generics, status
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserSerializer, UserProfileSerializer
from .models import UserProfile
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from django.contrib.auth.models import User
from .serializers import ChangePasswordSerializer
from rest_framework.views import APIView
from company.models import FinancialYears
from branches.models import BranchMaster
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import BranchMasterSerializer,UserProfileCreateSerializer
from company.serializers import FinancialYearsSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import SlidingToken

class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    # permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user).data,
            "message": "User created successfully"
        }, status=status.HTTP_201_CREATED)

class CreateUserProfileView(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    # permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Fetch user_id from request or default to the authenticated user
        user_id = request.data.get('user_id', None)
        
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        branches = request.data.get('branches')
        role = request.data.get('role')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        is_active = request.data.get('is_active')

        # Ensure branches and role are provided
        if not branches or not role:
            return Response(
                {"error": "Branches and role are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create or update the user profile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.branches.set(branches)
        user_profile.role = role
        user_profile.first_name = first_name
        user_profile.last_name = last_name
        user_profile.is_active = is_active
        user_profile.save()

        return Response({
            "message": "User profile created successfully",
            "user_profile": UserProfileSerializer(user_profile).data
        }, status=status.HTTP_201_CREATED)

class UpdateUserProfileView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    # permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Fetch user_id from the request data
        user_id = request.data.get('user_id', None)
        
        if not user_id:
            return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user exists
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user profile exists
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update fields based on request data
        branches = request.data.get('branches', None)
        role = request.data.get('role', None)
        first_name = request.data.get('first_name', None)
        last_name = request.data.get('last_name', None)
        is_active = request.data.get('is_active', None)

        if branches:
            try:
                branch_objs = BranchMaster.objects.filter(id__in=branches)
                if len(branch_objs) != len(branches):
                    return Response(
                        {"error": "One or more branches not found."}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                user_profile.branches.set(branch_objs)
            except Exception as e:
                return Response(
                    {"error": f"Error updating branches: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        if role is not None:
            user_profile.role = role
        if is_active is not None:
            user_profile.is_active = bool(is_active)
        if first_name is not None:
            user_profile.first_name=first_name
        if last_name is not None:            
            user_profile.last_name=last_name

        # Save the updated user profile
        user_profile.save()

        return Response({
            "message": "User profile updated successfully",
            "user_profile": UserProfileSerializer(user_profile).data
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LoginReverifyAPIView(APIView):
    permission_classes = [AllowAny]  # No authentication required

    def post(self, request, *args, **kwargs):
        # Extract data from the request
        username = request.data.get('username')
        password = request.data.get('password')
        financial_year_id = request.data.get('financial_year_id')
        branch_id = request.data.get('branch_id')

        # Step 1: Validate the user credentials
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({
                "status": "error",
                "msg": "Invalid username or password.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Check if the financial year exists and is active
        try:
            financial_year = FinancialYears.objects.get(
                id=financial_year_id, is_active=True)
        except FinancialYears.DoesNotExist:
            return Response({
                "status": "error",
                "msg": "Financial year not found or is not active.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 3: Check if the user is assigned to the provided branch
        try:
            user_profile = UserProfile.objects.get(user=user)
            branch = BranchMaster.objects.get(id=branch_id)
            if branch not in user_profile.branches.all():
                return Response({
                    "status": "error",
                    "msg": "User is not assigned to this branch.",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)
           
            if not user_profile.is_active:
                return Response({
                    "status": "error",
                    "msg": "Your account is inactive. Please contact the administrator.",
                    "data": None
                }, status=status.HTTP_403_FORBIDDEN)

        except BranchMaster.DoesNotExist:
            return Response({
                "status": "error",
                "msg": "Branch not found.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        except UserProfile.DoesNotExist:
            return Response({
                "status": "error",
                "msg": "User profile not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        # Step 4: Generate JWT token for the authenticated user
        # refresh = RefreshToken.for_user(user)
        # access_token = str(refresh.access_token)
        # refresh_token = str(refresh)

        token = SlidingToken.for_user(user)
        access_token = str(token) 

        # Step 5: Serialize branch and financial year data
        branch_data = BranchMasterSerializer(branch).data
        financial_year_data = FinancialYearsSerializer(financial_year).data
        role = user_profile.role
        # Step 6: Construct the response
        return Response({
            "status": "success",
            "msg": "Login successful.",
            "data": {
                "token": access_token,
                
                "branch": branch_data,
                "financial_year": financial_year_data,
                "role":role
            }
        }, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Set the new password for the authenticated user
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Get the requesting user's profile
            user_profile = UserProfile.objects.get(user=request.user)

            # Check if the requesting user is an admin
            if user_profile.role != 'admin':
                return Response(
                    {"error": "You do not have permission to reset passwords."},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get the target user ID and new password from the request
            user_id = request.data.get('user_id')
            new_password = request.data.get('new_password')

            if not user_id or not new_password:
                return Response(
                    {"error": "Both 'user_id' and 'new_password' are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch the target user by ID
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {"error": f"User with ID {user_id} does not exist."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Set the new password for the target user
            target_user.set_password(new_password)
            target_user.save()

            return Response(
                {"message": f"Password reset successfully for user ID {user_id}."},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserBranchesAPIView(generics.ListAPIView):
    serializer_class = BranchMasterSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        token = self.request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return BranchMaster.objects.none()  # No branches if no token is provided

        # Extract user from token
        user = self.request.user
        if not user.is_authenticated:
            return BranchMaster.objects.none()  # No branches if user is not authenticated

        return BranchMaster.objects.filter(user_profiles__user=user,is_active=True,flag=True)

class GetUserByIdView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')

        # Validate that user_id is provided
        if not user_id:
            return Response({
                "status": "error",
                "msg": "User ID is required.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user by ID
        try:
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "msg": "User not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({
                "status": "error",
                "msg": "User profile not found.",
                "data": None
            }, status=status.HTTP_404_NOT_FOUND)

        # Serialize the user profile data
        serialized_data = UserProfileSerializer(user_profile).data

        # Return the response
        return Response({
            "status": "success",
            "msg": "User details fetched successfully.",
            "data": serialized_data
        }, status=status.HTTP_200_OK)

class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        # Fetch all users
        queryset = User.objects.all()
        
        # Serialize the list of users
        serializer = UserSerializer(queryset, many=True)
        
        # Return the serialized data as a response
        return Response(serializer.data)