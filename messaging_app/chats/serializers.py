from rest_framework import serializers

from .models import Conversation, Message, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source="sender",
        write_only=True,
    )
    conversation = serializers.PrimaryKeyRelatedField(read_only=True)
    conversation_id = serializers.PrimaryKeyRelatedField(
        queryset=Conversation.objects.all(),
        source="conversation",
        write_only=True,
    )

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "conversation_id",
            "sender",
            "sender_id",
            "message_body",
            "sent_at",
        ]
        read_only_fields = ["id", "conversation", "sender", "sent_at"]


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        source="participants",
        write_only=True,
    )
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "participants",
            "participant_ids",
            "messages",
            "created_at",
        ]
        read_only_fields = ["id", "participants", "messages", "created_at"]

    def create(self, validated_data):
        participants = validated_data.pop("participants", [])
        conversation = super().create(validated_data)
        if participants:
            conversation.participants.set(participants)
        return conversation
