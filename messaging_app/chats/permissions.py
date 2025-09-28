"""Custom permissions for the chats app."""

from rest_framework import permissions


class IsConversationParticipant(permissions.BasePermission):
    """Allow access only to conversations or messages tied to the request user."""

    def has_permission(self, request, view):
        # Defer to object-level checks for detail routes; list routes still require auth.
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        conversation = getattr(obj, "conversation", obj)
        participants = getattr(conversation, "participants", None)
        if participants is None:
            return False
        return participants.filter(pk=request.user.pk).exists()
