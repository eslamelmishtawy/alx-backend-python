from rest_framework import filters, viewsets

from .models import Conversation, Message
from .permissions import IsConversationParticipant
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsConversationParticipant]
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
        base_queryset = Conversation.objects.all().prefetch_related(
            "participants",
            "messages__sender",
        )
        if not user or not user.is_authenticated:
            return base_queryset.none()
        return base_queryset.filter(participants=user)


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsConversationParticipant]
    serializer_class = MessageSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["sent_at"]
    ordering = ["sent_at"]

    def get_queryset(self):
        user = self.request.user
        base_queryset = Message.objects.all().select_related("conversation", "sender")
        if not user or not user.is_authenticated:
            return base_queryset.none()
        queryset = base_queryset.filter(conversation__participants=user)
        conversation_id = self.kwargs.get("conversation_pk") or self.request.query_params.get(
            "conversation"
        )
        if conversation_id:
            queryset = queryset.filter(conversation__id=conversation_id)
        return queryset
