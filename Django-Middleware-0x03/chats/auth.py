"""Authentication helpers and JWT views for the chats app."""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UserSerializer


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Issue JWT tokens and embed user metadata in the response payload."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
        token["role"] = getattr(user, "role", None)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(
            self.user,
            context=self.context,
        ).data
        return data


class UserTokenObtainPairView(TokenObtainPairView):
    """Return access/refresh tokens plus serialized user details."""

    serializer_class = UserTokenObtainPairSerializer


class UserTokenRefreshView(TokenRefreshView):
    """Allow clients to refresh access tokens using refresh tokens."""

    pass
