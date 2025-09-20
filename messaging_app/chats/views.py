from rest_framework import filters, viewsets

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all().prefetch_related(
        "participants",
        "messages__sender",
    )
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "participants__username",
        "participants__first_name",
        "participants__last_name",
        "participants__email",
    ]


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().select_related("conversation", "sender")
    serializer_class = MessageSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["sent_at"]
    ordering = ["sent_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        conversation_id = self.kwargs.get("conversation_pk") or self.request.query_params.get(
            "conversation"
        )
        if conversation_id:
            queryset = queryset.filter(conversation__id=conversation_id)
        return queryset
