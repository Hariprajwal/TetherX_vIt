# urbanSecurity_app/auth_views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User
from .auth_serializers import (
    RegisterSerializer, UserSerializer,
    PasswordChangeSerializer, AccountDeleteSerializer,
)
from .utils.smtp import send_otp_email


# ─────────────────────────────────────
# REGISTER — sends OTP email (no admin)
# ─────────────────────────────────────

class RegisterView(APIView):
    """POST: Register a new user → sends OTP email for verification."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()

        # Send OTP email
        try:
            send_otp_email(email=user.email, otp=user.verification_code)
        except Exception as e:
            # If email fails, still register but warn
            return Response({
                "message": "User registered but OTP email failed. Contact admin.",
                "user": UserSerializer(user).data,
                "email_error": str(e),
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "User registered. Check your email for the OTP verification code.",
            "user": UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


# ─────────────────────────────────────
# VERIFY OTP
# ─────────────────────────────────────

class VerifyView(APIView):
    """POST: Verify account with OTP code."""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        code = request.data.get("verification_code")

        if not username or not code:
            return Response(
                {"error": "Username and verification_code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.is_verified:
            return Response({"message": "Account is already verified."})

        if user.verification_code != str(code):
            return Response(
                {"error": "Invalid verification code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_verified = True
        user.verification_code = None  # Clear code after use
        user.save()

        # Auto-issue JWT tokens after verification
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Account verified successfully.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        })


# ─────────────────────────────────────
# RESEND OTP
# ─────────────────────────────────────

class ResendOTPView(APIView):
    """POST: Resend OTP to user's email."""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        if not username:
            return Response({"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.is_verified:
            return Response({"message": "Account is already verified."})

        user.generate_code()
        try:
            send_otp_email(email=user.email, otp=user.verification_code)
        except Exception as e:
            return Response({"error": f"Failed to send OTP: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "OTP resent successfully. Check your email."})


# ─────────────────────────────────────
# LOGIN — custom JWT (admin = superuser)
# ─────────────────────────────────────

class LoginView(APIView):
    """
    POST: Login with username + password.
    - Admin: Django superuser credentials → auto verified, full access
    - Others: must be email-verified first
    Returns JWT access + refresh tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Admin (superuser) bypasses email verification
        if not user.is_superuser and not user.is_verified:
            return Response(
                {"error": "Account not verified. Check your email for the OTP.", "needs_verification": True, "username": user.username},
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
        })


# ─────────────────────────────────────
# CURRENT USER
# ─────────────────────────────────────

class CurrentUserView(APIView):
    """GET: Returns the current authenticated user's info."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# ─────────────────────────────────────
# PASSWORD CHANGE
# ─────────────────────────────────────

class PasswordChangeView(APIView):
    """POST: Change the authenticated user's password."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(serializer.validated_data['current_password']):
            return Response(
                {"current_password": ["Current password is incorrect."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)


# ─────────────────────────────────────
# ACCOUNT DELETE
# ─────────────────────────────────────

class AccountDeleteView(APIView):
    """POST: Permanently delete the authenticated user's account."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AccountDeleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.check_password(serializer.validated_data['password']):
            return Response(
                {"password": ["Password is incorrect."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.delete()
        return Response({"message": "Account deleted permanently."}, status=status.HTTP_200_OK)


# ─────────────────────────────────────
# CHECK USERNAME / EMAIL AVAILABILITY
# ─────────────────────────────────────

class CheckUsernameView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        username = request.query_params.get('username', '')
        if not username:
            return Response({"available": False, "message": "Username required"})
        exists = User.objects.filter(username__iexact=username).exists()
        return Response({
            "available": not exists,
            "message": "Username is taken" if exists else "Username is available"
        })


class CheckEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get('email', '')
        if not email:
            return Response({"available": False, "message": "Email required"})
        exists = User.objects.filter(email__iexact=email).exists()
        return Response({
            "available": not exists,
            "message": "Email already registered" if exists else "Email is available"
        })
