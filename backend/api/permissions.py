from rest_framework import permissions


class AdminOrAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method == 'POST' 
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if (request.method in ['PUT', 'PATCH', 'DELETE']
                and not request.user.is_anonymous):
            return (
                request.user == obj.author
                or request.user.is_superuser
                or request.user.is_admin()
            )
        return request.method in permissions.SAFE_METHODS
