from django.urls import path
from .views import *
from .sms_views import RequestOTPView, VerifyOTPView

urlpatterns = [
    # New SMS Authentication Endpoints
    path('sms/request-otp/', RequestOTPView.as_view(), name='request_otp'),
    path('sms/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),

    # Existing Email-based Endpoints
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/',LogoutAPIView.as_view(), name='logout'),
    path('activate-email/<str:uidb64>/<str:token>/', ActivateEmailAPIView.as_view(), name='activate_email'),
    path('password-reset/', PasswordResetAPIView.as_view(), name='password_reset'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
    path('password-change/<str:uidb64>/<str:token>/', PasswordChangeAPIView.as_view(), name='password_change'),
    path('search/', SearchUserView.as_view(), name='search_user'),
    path('delete-account/', DeleteAccountAPIView.as_view(), name='delete_account'),
    path('login-verify/<str:otp>/', OTPVerifyAPIView.as_view(), name='otp_verify'),
    path('change-password/', change_password, name='change_password'),
    path('resend-activation-email/', ResendActivationEmailAPIView.as_view(), name='resend_activation_email'),
    path('resend-otp/', ResendOTPAPIView.as_view(), name='resend_otp'),
    path('token/refresh-both/', RefreshTokenAPIView.as_view(), name='token_refresh'),
    path('create-admin/', CreatSuperUserView.as_view(), name='create-admin'),

    path('simplelogin/', SimpleLoginAPIView.as_view(), name='login'),
]