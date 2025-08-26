from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import timedelta
import random

from .models import User
from .utils import send_sms
from rest_framework_simplejwt.tokens import RefreshToken

class RequestOTPView(APIView):
    """
    View to request an OTP for a given phone number.
    If the user doesn't exist, a new user is created.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Basic validation for phone number format could be done here with a serializer
        # but for now we rely on the model's validator.

        try:
            # Using get_or_create with defaults to handle new user creation atomically and safely.
            user, created = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={'username': phone_number}
            )

            # Generate a 6-digit OTP
            otp_code = random.randint(100000, 999999)

            # Save OTP and its expiration time (e.g., 5 minutes)
            user.otp = str(otp_code)
            user.otp_expiration = timezone.now() + timedelta(minutes=5)
            user.save()

            # Send the OTP via SMS (or print to console in debug mode)
            if send_sms(user.phone_number, otp_code):
                return Response({'message': 'OTP has been sent to your phone number.'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to send OTP. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            # This will catch validation errors from the model (e.g., invalid phone format)
            # or any other unexpected errors.
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in RequestOTPView: {e}", exc_info=True)
            return Response({'error': 'An unexpected error occurred. Please check server logs.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    """
    View to verify the OTP and log the user in by returning JWT tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        otp_code = request.data.get('otp')

        if not phone_number or not otp_code:
            return Response({'error': 'Phone number and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({'error': 'User with this phone number does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the OTP is correct and not expired
        if user.otp == otp_code and user.is_otp_valid():
            # OTP is correct. Activate the user if they are new.
            if not user.is_active:
                user.is_active = True

            # Clear the OTP fields after successful verification
            user.otp = None
            user.otp_expiration = None
            user.save()

            # Generate JWT tokens for the user
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Login successful!',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)
