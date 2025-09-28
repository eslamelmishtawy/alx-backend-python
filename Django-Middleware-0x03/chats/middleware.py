"""Middleware for logging, access control, and rate limiting."""

from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils import timezone


class RequestLoggingMiddleware:
    """Log every request with timestamp, user, and path."""

    def __init__(self, get_response):
        self.get_response = get_response
        log_path = Path(settings.BASE_DIR) / "requests.log"
        self.log_file = log_path
        if not self.log_file.exists():
            self.log_file.touch()

    def __call__(self, request):
        response = self.get_response(request)
        user = request.user if request.user.is_authenticated else "Anonymous"
        entry = f"{datetime.now().isoformat()} - User: {user} - Path: {request.path}\n"
        with self.log_file.open("a", encoding="utf-8") as fh:
            fh.write(entry)
        return response


class RestrictAccessByTimeMiddleware:
    """Deny access outside the 6 AM – 9 PM window."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.start_hour = 6
        self.end_hour = 21

    def __call__(self, request):
        now = timezone.localtime()
        if not (self.start_hour <= now.hour < self.end_hour):
            return HttpResponseForbidden("Access restricted between 9 PM and 6 AM.")
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """Limit POST requests (messages) per IP within a rolling time window."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.window = timedelta(minutes=1)
        self.limit = 5
        self.history = defaultdict(deque)

    def __call__(self, request):
        if request.method == "POST" and request.path.startswith("/api/messages"):
            ip_address = self._get_client_ip(request)
            now = timezone.now()
            timestamps = self.history[ip_address]
            while timestamps and now - timestamps[0] > self.window:
                timestamps.popleft()
            if len(timestamps) >= self.limit:
                return HttpResponseForbidden("Message rate limit exceeded. Please wait before sending more messages.")
            timestamps.append(now)
        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class RolepermissionMiddleware:
    """Ensure only privileged roles perform modifying API actions."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_roles = {"admin", "moderator"}
        self.protected_methods = {"POST", "PUT", "PATCH", "DELETE"}

    def __call__(self, request):
        if request.path.startswith("/api/") and request.method in self.protected_methods:
            user = getattr(request, "user", None)
            role = getattr(user, "role", "") if user and user.is_authenticated else None
            if role not in self.allowed_roles:
                return HttpResponseForbidden("You do not have permission to perform this action.")
        return self.get_response(request)
