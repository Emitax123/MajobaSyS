"""
Permisos personalizados para la API REST de MajobaSyS.
"""
from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permite acceso solo al propietario del recurso.
    El recurso debe tener un campo 'user' que sea FK al usuario.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsStaffOrOwner(permissions.BasePermission):
    """
    Permite acceso a staff o al propietario del recurso.
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user


class IsStaffUser(permissions.BasePermission):
    """
    Permite acceso solo a usuarios staff.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff
