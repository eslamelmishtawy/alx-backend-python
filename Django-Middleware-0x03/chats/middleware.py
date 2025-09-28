"""Middleware for logging user requests."""

from datetime import datetime
from pathlib import Path

from django.conf import settings


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
