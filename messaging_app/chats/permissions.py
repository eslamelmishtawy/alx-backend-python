"""Custom permissions for the chats app."""

from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """Allow authenticated participants to interact with conversation data."""

    def has_permission(self, request, view):
        # Ensure the requester is authenticated before reaching object checks.
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        conversation = getattr(obj, "conversation", obj)
        participants = getattr(conversation, "participants", None)
        if participants is None:
            return False
        is_participant = participants.filter(pk=request.user.pk).exists()
        if request.method in {"PUT", "PATCH", "DELETE"}:
            return is_participant
        if request.method in permissions.SAFE_METHODS:
            return is_participant
        return is_participant
