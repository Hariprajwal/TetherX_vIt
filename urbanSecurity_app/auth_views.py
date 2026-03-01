# urbanSecurity_app/auth_views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User

from .auth_serializers import (
    RegisterSerializer, UserSerializer,
    PasswordChangeSerializer, AccountDeleteSerializer,
)


class RegisterView(APIView):
    """POST: Register a new user with username, email, password, role."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
                "user": UserSerializer(user).data,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(APIView):
    """GET: Returns the current authenticated user's info."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


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


class CheckUsernameView(APIView):
    """GET: Check if a username is available."""
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
    """GET: Check if an email is available."""
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
