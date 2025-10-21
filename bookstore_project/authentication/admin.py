from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserActivity

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action', 'ip_address')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
