import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Application user with UUID primary key and contact metadata."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    class Role(models.TextChoices):
        GUEST = "guest", "Guest"
        HOST = "host", "Host"
        ADMIN = "admin", "Admin"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.GUEST,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - human readable helper
        return self.email or self.username

    @property
    def user_id(self) -> uuid.UUID:
        """Expose a stable identifier expected by external consumers."""

        return self.id

    def has_password_set(self) -> bool:
        """Mirror Django's password presence for specification checks."""

        return bool(self.password)

    @property
    def full_name(self) -> str:
        """Convenience accessor for first/last name combinations."""

        return f"{self.first_name} {self.last_name}".strip()


class Conversation(models.Model):
    """Group together users participating in a discussion."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - human readable helper
        return f"Conversation {self.id}"

    @property
    def conversation_id(self) -> uuid.UUID:
        """Expose field name expected by external schemas."""

        return self.id


class Message(models.Model):
    """A message sent by a user inside a conversation."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_sent",
    )
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sent_at"]

    def __str__(self) -> str:  # pragma: no cover - human readable helper
        return f"Message {self.id}"

    @property
    def message_id(self) -> uuid.UUID:
        """Expose field name expected by external schemas."""

        return self.id
