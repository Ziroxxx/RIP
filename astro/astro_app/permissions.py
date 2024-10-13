from rest_framework import permissions
from .getUser import getUserBySession

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySession(request)
        print(f"User in permission checkk: {user}")
        return bool(user and (user.is_staff or user.is_superuser))

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySession(request)
        return bool(user and user.is_superuser)
    
class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySession(request)
        print(f"User in permission check: {request.user}")
        return bool(user)
    
class IsAuthOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySession(request)
        return bool(user) or request.method in permissions.SAFE_METHODS