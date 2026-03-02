# urbanSecurity_app/auth_serializers.py
import re
from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """Register with roles: viewer, Engineer, Municipal (NO admin)."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(
        choices=[('viewer', 'Viewer'), ('Engineer', 'Engineer'), ('Municipal', 'Municipal')],
        default='viewer',
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'role']

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters.")
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        # Block admin role
        if data.get('role', '').lower() == 'admin':
            raise serializers.ValidationError({"role": "Admin role cannot be registered."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        role = validated_data.pop('role', 'viewer')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role,
            is_verified=False,
        )
        user.generate_code()  # Generate OTP
        return user


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_verified', 'date_joined', 'last_login']

    def get_role(self, obj):
        return obj.get_effective_role()


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, min_length=8)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', value):
            raise serializers.ValidationError("Must contain at least one special character.")
        return value

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Passwords do not match."})
        return data


class AccountDeleteSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    confirmation = serializers.CharField(required=True)

    def validate_confirmation(self, value):
        if value != 'DELETE MY ACCOUNT':
            raise serializers.ValidationError("Please type 'DELETE MY ACCOUNT' to confirm.")
        return value
