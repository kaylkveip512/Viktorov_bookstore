from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', views.RefreshTokenView.as_view(), name='refresh-token'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('check-auth/', views.CheckAuthView.as_view(), name='check-auth'),
]
