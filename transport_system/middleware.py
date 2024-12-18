from django.shortcuts import redirect
from django.urls import reverse
import time
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import SlidingToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from datetime import timedelta,datetime, timedelta
from django.conf import settings
import pytz

class RedirectAdminLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/admin/login/' and not request.user.is_authenticated:
            return redirect(reverse('login'))
        response = self.get_response(request)
        return response

class RefreshSlidingTokenMiddleware(MiddlewareMixin):
    def __call__(self, request):
        response = self.get_response(request)

        # Check if the user is authenticated and if the request contains an Authorization header
        if request.user.is_authenticated and 'Authorization' in request.headers:
            auth_header = request.headers['Authorization'].split()
            if len(auth_header) == 2 and auth_header[0].lower() == 'bearer':
                token = auth_header[1]
                try:
                    # Decode the token to check the expiration
                    sliding_token = SlidingToken(token)
                    
                    # Convert token 'exp' field to a datetime object
                    exp_timestamp = sliding_token['exp']
                    exp_time = datetime.fromtimestamp(exp_timestamp, pytz.UTC)

                    # Calculate how much time is left until token expiration
                    time_left = exp_time - sliding_token.current_time

                    # Refresh the token if it's close to expiration (e.g., less than 1 minute left)
                    if time_left <= timedelta(minutes=5):
                        # Issue a new sliding token for the user
                        new_token = SlidingToken.for_user(request.user)
                        # Add the new token to the response headers
                        response['Authorization'] = f'Bearer {str(new_token)}'

                except (InvalidToken, TokenError) as e:
                    # If the token is invalid or has an issue, continue without refreshing it
                    pass

        return response