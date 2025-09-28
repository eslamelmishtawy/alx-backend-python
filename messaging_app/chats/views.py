from rest_framework import filters, permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN

from .models import Conversation, Message
from .permissions import IsParticipantOfConversation
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "participants__username",
        "participants__first_name",
        "participants__last_name",
        "participants__email",
    ]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Conversation.objects.none()
        return (
            Conversation.objects.filter(participants=user)
            .prefetch_related("participants", "messages__sender")
            .distinct()
        )


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    serializer_class = MessageSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["sent_at"]
    ordering = ["sent_at"]

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Message.objects.none()
        queryset = Message.objects.filter(conversation__participants=user).select_related(
            "conversation",
            "sender",
        )
        conversation_id = self.kwargs.get("conversation_pk") or self.request.query_params.get(
            "conversation"
        )
        if conversation_id:
            queryset = queryset.filter(conversation__id=conversation_id)
        return queryset

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get("conversation") or request.data.get("conversation_id")
        if conversation_id and not Conversation.objects.filter(
            id=conversation_id,
            participants=request.user,
        ).exists():
            return Response(
                {"detail": "You are not allowed to send messages in this conversation."},
                status=HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        sender = serializer.validated_data.get("sender")
        if sender != self.request.user:
            raise PermissionDenied("You can only send messages as yourself.")
        serializer.save()
