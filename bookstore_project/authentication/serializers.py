from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from .models import CustomUser, UserActivity
import re
import logging

logger = logging.getLogger(__name__)

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        min_length=8, 
        max_length=128,
        style={'input_type': 'password'}
    )
    password_check = serializers.CharField(
        write_only=True, 
        min_length=8, 
        max_length=128,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'password_check')
        extra_kwargs = {
            'username': {'max_length': 50},
            'first_name': {
                'max_length': 30, 
                'required': False, 
                'allow_blank': True
            },
            'last_name': {
                'max_length': 30, 
                'required': False, 
                'allow_blank': True
            },
            'email': {'max_length': 254}
        }
    
    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers and underscores.")
        return value
    
    def validate_email(self, value):
        validator = EmailValidator()
        try:
            validator(value)
        except:
            logger.warning(f"Invalid email format attempted: {value}")
            raise serializers.ValidationError("Enter a valid email address.")
        
        if CustomUser.objects.filter(email=value).exists():
            logger.warning(f"Registration attempt with existing email: {value}")
            raise serializers.ValidationError("A user with this email already exists.")
        
        return value
    
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        
        try:
            validate_password(value)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        return value
    
    def validate(self, data):
        if data['password'] != data['password_check']:
            logger.warning("Password mismatch during registration")
            raise serializers.ValidationError({"password_check": "Passwords do not match."})

        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: "This field is required."})
        
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_check')
        password = validated_data.pop('password')
        
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        logger.info(f"User created successfully: {user.username}")
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'date_joined')
        read_only_fields = ('id', 'is_staff', 'date_joined')
        extra_kwargs = {
            'username': {'max_length': 50},
            'first_name': {'max_length': 30},
            'last_name': {'max_length': 30},
            'email': {'max_length': 254}
        }


class UserActivitySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = ('id', 'username', 'action', 'timestamp', 'ip_address', 'user_agent')
        read_only_fields = ('id', 'username', 'timestamp')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(
        max_length=128,
        style={'input_type': 'password'}
    )
    
    def validate_username(self, value):
        if not value:
            raise serializers.ValidationError("Username is required.")
        return value
    
    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password is required.")
        return value

class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
