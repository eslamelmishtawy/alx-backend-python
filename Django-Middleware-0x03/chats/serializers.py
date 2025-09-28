from rest_framework import serializers

from .models import Conversation, Message, User


class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source="user_id", read_only=True)

    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "created_at",
        ]
        read_only_fields = ["user_id", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    message_id = serializers.UUIDField(source="message_id", read_only=True)
    message_body = serializers.CharField()
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
            "message_id",
            "conversation",
            "conversation_id",
            "sender",
            "sender_id",
            "message_body",
            "sent_at",
        ]
        read_only_fields = [
            "message_id",
            "conversation",
            "sender",
            "sent_at",
        ]

    def validate(self, attrs):
        conversation = attrs.get("conversation")
        sender = attrs.get("sender")
        if (
            conversation
            and sender
            and not conversation.participants.filter(pk=sender.pk).exists()
        ):
            raise serializers.ValidationError(
                "Sender must be a participant in the conversation."
            )
        return attrs


class ConversationSerializer(serializers.ModelSerializer):
    conversation_id = serializers.UUIDField(
        source="conversation_id",
        read_only=True,
    )
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        source="participants",
        write_only=True,
    )
    messages = MessageSerializer(many=True, read_only=True)
    latest_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "participant_ids",
            "messages",
            "latest_message",
            "created_at",
        ]
        read_only_fields = [
            "conversation_id",
            "participants",
            "messages",
            "latest_message",
            "created_at",
        ]

    def create(self, validated_data):
        participants = validated_data.pop("participants", [])
        conversation = super().create(validated_data)
        if participants:
            conversation.participants.set(participants)
        return conversation

    def get_latest_message(self, obj):
        message = obj.messages.order_by("-sent_at").first()
        if not message:
            return None
        return MessageSerializer(message, context=self.context).data
