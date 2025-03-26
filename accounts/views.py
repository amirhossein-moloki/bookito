from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str, force_bytes
from .models import User
from django.http import Http404, HttpResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer
from django.contrib.auth.forms import PasswordResetForm
from django_ratelimit.decorators import ratelimit
from django.template.loader import render_to_string
import logging
import random
import string
from django.utils import timezone
from datetime import timedelta, datetime
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.decorators import api_view, permission_classes

logger = logging.getLogger(__name__)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Validate input data using the serializer
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Save the user using the serializer
            user = serializer.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Generate email verification token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())
            # Updated verification link with email as a query parameter
            verification_link = f'https://fortify-frontend.vercel.app/activate-email?uid={uid}&token={token}&email={user.email}'  # Include user email in the URL

            # Define URLs for login and forgot password
            login_action_url = 'https://fortify-frontend.vercel.app/login'  # Use https in production
            forgot_password_url = 'https://fortify-frontend.vercel.app/forgot-password'  # Use https in production

            email_subject = 'Welcome to Fortify - Confirm Your Email'

            # Generate the email HTML content
            try:
                email_message = render_to_string('activation_email.html', {
                    'verification_link': verification_link,
                    'support_email': 'support@example.com',
                    'user_name': user.username,
                    'login_action_url': login_action_url,
                    'forgot_password_url': forgot_password_url,
                    'user_email': user.email  # Added user email to the content of the email
                })

                # Send the email to the user
                send_mail(
                    email_subject,
                    '',  # No plain text as it's HTML email
                    'no-reply@fortify.com',  # Sender's email
                    [user.email],  # Send to the user's email
                    fail_silently=False,
                    html_message=email_message  # Send the HTML content
                )

            except Exception as e:
                logger.error(f"Error sending email: {e}")
                return Response({"message": "Error sending confirmation email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Return the response to the client
            return Response({
                "message": "Please confirm your email address to complete the registration.",
                "access_token": access_token
            }, status=status.HTTP_201_CREATED)

        # If serializer is not valid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def generate_otp(self, length=6):
        """ تولید یک کد OTP تصادفی """
        characters = string.ascii_letters + string.digits
        otp = ''.join(random.choice(characters) for i in range(length))
        return otp

    def post(self, request):
        # استفاده از سریالایزر برای اعتبارسنجی داده‌ها
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')

            # تلاش برای شناسایی کاربر با نام کاربری و رمز عبور
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    # تولید کد OTP برای ورود
                    otp = self.generate_otp()

                    # ذخیره OTP و تاریخ انقضا (10 دقیقه)
                    user.otp = otp
                    user.otp_expiration = timezone.now() + timedelta(minutes=10)  # تغییر در این خط
                    user.save()

                    otp_link = f'https://fortify-frontend.vercel.app/otp/otp={otp}'
                    email_subject = 'Login Attempt - OTP Verification'
                    email_message = render_to_string('otp_email.html', {
                        'otp': otp,
                        'user_name': user.username,
                        'otp_link': otp_link,
                        'support_email': 'support@yourdomain.com',
                    })

                    send_mail(
                        email_subject,
                        '',  # متن ساده را خالی می‌گذاریم چون فقط قالب HTML ارسال می‌شود.
                        'no-reply@yourdomain.com',
                        [user.email],
                        fail_silently=False,
                        html_message=email_message
                    )

                    return Response({
                        "message": "Login successful! Please check your email for the OTP link."
                    }, status=status.HTTP_200_OK)

                else:
                    return Response({
                        "message": "Account is not active. Please check your email for activation."
                    }, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "message": "Invalid credentials."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# ویو تایید ایمیل
class ActivateEmailAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            # دیکد کردن شناسه کاربر
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            # بررسی توکن تأیید
            if default_token_generator.check_token(user, token):
                # فعال کردن کاربر
                user.is_active = True
                user.save()

                # ایجاد توکن‌های جدید برای دسترسی و رفرش
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)

                # ارسال پاسخ موفقیت و توکن‌ها
                return Response({
                    "message": "Email successfully confirmed!",
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"message": "Invalid token or user does not exist."}, status=status.HTTP_400_BAD_REQUEST)

# ویو برای بازیابی رمز عبور
class PasswordResetAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"message": "If an account exists with this email, a password reset link has been sent."}, status=status.HTTP_200_OK)

        # تولید توکن JWT
        refresh = RefreshToken.for_user(user)
        reset_token = str(refresh.access_token)

        # لینک بازنشانی رمز عبور
        reset_link = f'https://fortify-frontend.vercel.app/password-reset/{urlsafe_base64_encode(force_bytes(user.pk))}/{reset_token}/'

        # ارسال ایمیل
        email_subject = 'Password Reset'
        email_message = render_to_string('reset_password_email.html', {
            'reset_link': reset_link,
            'support_email': 'support@yourdomain.com',
            'user_name': user.username,
        })

        send_mail(
            email_subject,
            '',  # محتوای متنی
            'no-reply@yourdomain.com',
            [user.email],
            fail_silently=False,
            html_message=email_message  # محتوای HTML
        )

        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)

# ویو تایید بازیابی رمز عبور
class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            # بررسی توکن JWT
            try:
                AccessToken(token)  # بررسی اعتبار توکن
            except TokenError:
                return Response({"message": "Token is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)

            # تنظیم رمز عبور جدید
            new_password = request.data.get('password')
            if new_password:
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Password not provided."}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"message": "Invalid user."}, status=status.HTTP_400_BAD_REQUEST)

# ویو برای تغییر رمز عبور
class PasswordChangeAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, uidb64, token):
        password = request.data.get('password')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))  # تبدیل رشته به force_str
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                return Response({"message": "Password changed successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"message": "Invalid token or user does not exist."}, status=status.HTTP_400_BAD_REQUEST)



# ویو برای خروج کاربر
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # غیرفعال کردن توکن
            return Response({"message": "Logout successful!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


# ویو برای حذف حساب کاربری
class DeleteAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        user = request.user
        user.delete()
        return Response({"message": "Account deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

class OTPVerifyAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, otp):
        try:
            # جستجوی کاربر بر اساس کد OTP
            user = User.objects.get(otp=otp)

            # بررسی زمان انقضای OTP
            if not user.otp_expiration or user.otp_expiration < timezone.now():
                return Response({
                    "message": "OTP expired or invalid. Please request a new one."
                }, status=status.HTTP_400_BAD_REQUEST)

            # بررسی اعتبار OTP
            if user.is_otp_valid():
                # اعتبار سنجی موفق
                # ایجاد توکن JWT
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token

                # پس از ورود، OTP پاک می‌شود
                user.otp = None  # OTP را پاک می‌کنیم
                user.otp_expiration = None  # انقضای OTP را پاک می‌کنیم
                user.save()

                # بازگرداندن توکن‌ها و نام کاربری در پاسخ
                return Response({
                    "message": "Login successful!",
                    "access_token": str(access_token),
                    "refresh_token": str(refresh),
                    "username": user.username  # اضافه کردن نام کاربری به پاسخ
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    "message": "Invalid OTP."
                }, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({
                "message": "User not found or invalid OTP."
            }, status=status.HTTP_400_BAD_REQUEST)






class SearchUserView(APIView):
    def get(self, request):
        username = request.query_params.get('username', None)
        email = request.query_params.get('email', None)

        # جستجو بر اساس username
        if username:
            try:
                user = User.objects.get(username=username)
                user_serializer = UserSerializer(user)
                return Response(user_serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'detail': 'User not found with this username.'}, status=status.HTTP_404_NOT_FOUND)

        # جستجو بر اساس email
        elif email:
            try:
                user = User.objects.get(email=email)
                user_serializer = UserSerializer(user)
                return Response(user_serializer.data, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'detail': 'User not found with this email.'}, status=status.HTTP_404_NOT_FOUND)

        # اگر هیچ پارامتر جستجویی مشخص نشده باشد
        return Response({'detail': 'Please provide either a username or an email.'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change password for the authenticated user and refresh JWT token
    """
    user = request.user
    old_password = request.data.get("old_password")
    new_password = request.data.get("new_password")

    # Verify the old password
    if not user.check_password(old_password):
        return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

    # Update the password
    if new_password:
        user.set_password(new_password)
        user.save()

        # Invalidate old tokens by issuing new ones
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Password changed successfully.",
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)


class ResendActivationEmailAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email, is_active=False)

            # Generate new activation token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = f'https://fortify-frontend.vercel.app/api/accounts/activate-email?uid={uid}&token={token}&email={user.email}'

            # Define URLs for login and forgot password
            login_action_url = 'https://fortify-frontend.vercel.app/login'  # Use https in production
            forgot_password_url = 'https://fortify-frontend.vercel.app/forgot-password'  # Use https in production

            email_subject = 'Fortify - Resend Email Activation'
            email_message = render_to_string('activation_email.html', {
                'verification_link': verification_link,
                'support_email': 'support@example.com',
                'user_name': user.username,
                'login_action_url': login_action_url,
                'forgot_password_url': forgot_password_url,
                'user_email': user.email
            })

            send_mail(
                email_subject,
                '',  # No plain text as it's HTML email
                'no-reply@fortify.com',
                [user.email],
                fail_silently=False,
                html_message=email_message
            )

            return Response({"message": "Activation email resent successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "No inactive user found with this email."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error resending activation email: {e}")
            return Response({"message": "Error resending activation email."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)

            # Generate new OTP
            otp = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
            user.otp = otp
            user.otp_expiration = timezone.now() + timedelta(minutes=10)
            user.save()

            otp_link = f'https://fortify-frontend.vercel.app/otp/otp={otp}'
            email_subject = 'Fortify - New OTP for Login'
            email_message = render_to_string('otp_email.html', {
                'otp': otp,
                'user_name': user.username,
                'otp_link': otp_link,
                'support_email': 'support@yourdomain.com',
            })

            send_mail(
                email_subject,
                '',
                'no-reply@yourdomain.com',
                [user.email],
                fail_silently=False,
                html_message=email_message
            )

            return Response({"message": "New OTP sent successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "No user found with this username."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error resending OTP: {e}")
            return Response({"message": "Error sending new OTP."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RefreshTokenAPIView(APIView):
    """
    This view checks the remaining lifetime of the refresh token.
    If it's close to expiration, it generates a new refresh token along with the access token.
    Otherwise, only a new access token is issued.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response({"message": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate the provided refresh token
            refresh = RefreshToken(refresh_token)

            # Check the expiration time of the refresh token
            expiration = datetime.fromtimestamp(refresh['exp'], tz=timezone.utc)
            remaining_time = expiration - datetime.now(timezone.utc)

            # Define threshold for issuing a new refresh token
            threshold = timedelta(hours=1)  # Issue a new refresh token if less than 1 hour remains

            # Generate tokens
            new_access_token = str(refresh.access_token)
            response_data = {"access_token": new_access_token}

            if remaining_time < threshold:
                # If the remaining time is less than the threshold, issue a new refresh token
                new_refresh_token = str(refresh)
                response_data["refresh_token"] = new_refresh_token

            return Response(response_data, status=status.HTTP_200_OK)

        except TokenError:
            return Response({"message": "Invalid or expired refresh token."}, status=status.HTTP_401_UNAUTHORIZED)


class CreatSuperUserView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        def get(self, request):
            # بررسی کنید که آیا کاربر ادمین قبلاً وجود دارد یا نه
            if not User.objects.filter(username='admin').exists():
                # ایجاد کاربر ادمین جدید
                User.objects.create_superuser('AdminAmir', 'amir.moloki8558@gmail.com', 'h@rad140252')
                return HttpResponse("Admin user created successfully.")
            else:
                return HttpResponse("Admin user already exists.")


from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny

class SimpleLoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]
