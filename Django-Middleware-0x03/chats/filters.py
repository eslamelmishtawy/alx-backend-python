"""Filter classes for the chats API."""

import django_filters

from .models import Message


class MessageFilter(django_filters.FilterSet):
    """Filter messages by participant involvement and time bounds."""

    participant = django_filters.UUIDFilter(
        field_name="conversation__participants",
        lookup_expr="exact",
    )
    sent_after = django_filters.IsoDateTimeFilter(
        field_name="sent_at",
        lookup_expr="gte",
    )
    sent_before = django_filters.IsoDateTimeFilter(
        field_name="sent_at",
        lookup_expr="lte",
    )

    class Meta:
        model = Message
        fields = [
            "participant",
            "sent_after",
            "sent_before",
            "conversation",
            "sender",
        ]
