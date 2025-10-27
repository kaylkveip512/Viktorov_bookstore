from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        has_perm = request.user and request.user.is_staff
        if not has_perm:
            logger.warning(f"Admin permission denied for user: {getattr(request.user, 'username', 'Anonymous')}")
        return has_perm

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'user'):
            is_owner = obj.user == request.user
        else:
            is_owner = obj == request.user
        
        if not is_owner:
            logger.warning(f"Object access denied for user: {request.user.username}")
        return is_owner

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'owner'):
            is_owner = obj.owner == request.user
        elif hasattr(obj, 'user'):
            is_owner = obj.user == request.user
        else:
            is_owner = obj == request.user
        
        if not is_owner:
            logger.warning(f"Write permission denied for user: {request.user.username}")
        
        return is_owner
