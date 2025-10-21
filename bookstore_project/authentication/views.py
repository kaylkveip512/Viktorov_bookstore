from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import logging

from .models import CustomUser, UserActivity
from .serializers import RegistrationSerializer, UserSerializer
from .permissions import IsAdminUser, IsOwnerOrAdmin

logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        logger.info("Registration attempt")
        
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            UserActivity.objects.create(user=user, action="registration")
            return Response({'message': 'User registered successfully', 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        
        logger.warning(f"Registration failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        logger.info("Login attempt")
        
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            logger.warning("Login failed: Missing credentials")
            return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        if user is None:
            logger.warning(f"Login failed: Invalid credentials for username: {username}")
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        
        UserActivity.objects.create(user=user, action="login")
        
        logger.info(f"User logged in successfully: {username}")
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logger.info(f"Refresh token blacklisted for user: {request.user.username}")
            
            UserActivity.objects.create(user=request.user, action="logout")
            
            logger.info(f"User logged out: {request.user.username}")
            
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
            
        except TokenError as e:
            logger.error(f"Token error during logout: {str(e)}")
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error during logout: {str(e)}")
            return Response({'error': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                logger.warning("Refresh token missing")
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            
            user_id = token['user_id']
            user = CustomUser.objects.get(id=user_id)
            
            new_access_token = str(token.access_token)
            
            logger.info(f"Token refreshed for user: {user.username}")
            
            return Response({'access': new_access_token}, status=status.HTTP_200_OK)
            
        except TokenError as e:
            logger.error(f"Token error during refresh: {str(e)}")
            return Response(
                {'error': 'Invalid or expired refresh token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        except CustomUser.DoesNotExist:
            logger.error(f"User not found during token refresh")
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        logger.info(f"Profile accessed by user: {request.user.username}")
        return Response(UserSerializer(request.user).data)

class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        logger.info(f"Admin dashboard accessed by: {request.user.username}")
        
        user_count = CustomUser.objects.count()
        recent_activities = UserActivity.objects.select_related('user').order_by('-timestamp')[:10]
        
        activities_data = []
        for activity in recent_activities:
            activities_data.append({
                'username': activity.user.username,
                'action': activity.action,
                'timestamp': activity.timestamp
            })
        
        return Response({
            'total_users': user_count,
            'recent_activities': activities_data
        })

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            logger.warning(f"User not found with ID: {pk}")
            return None
    
    def get(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not (request.user.is_staff or request.user == user):
            logger.warning(f"Unauthorized access attempt to user {pk} by {request.user.username}")
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        logger.info(f"User detail accessed: {user.username} by {request.user.username}")
        return Response(UserSerializer(user).data)
    
    def put(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response({
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not (request.user.is_staff or request.user == user):
            logger.warning(f"Unauthorized update attempt to user {pk} by {request.user.username}")
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        logger.info(f"User update attempt: {user.username} by {request.user.username}")
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            action = "self_update" if request.user == user else f"updated_by_admin_{request.user.username}"
            UserActivity.objects.create(user=user, action=action)
            
            logger.info(f"User updated successfully: {user.username}")
            return Response(serializer.data)
        
        logger.warning(f"User update failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckAuthView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'isAuthenticated': True,
            'user': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)
