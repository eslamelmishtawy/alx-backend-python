"""Middleware for logging and access control."""

from datetime import datetime
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
