import logging

from django.conf import settings
from django.shortcuts import render

logger = logging.getLogger("sprigai")


class FriendlyErrorMiddleware:
    """
    Catches unhandled exceptions raised inside views (e.g. AI model loading
    failures, malformed uploads) and renders a friendly error page instead
    of leaking a raw Python traceback to end users. Full details are always
    logged server-side via logger.exception.

    In DEBUG mode, Django's own debug page still takes priority so
    developers can see full tracebacks locally.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.exception("Unhandled exception on %s: %s", request.path, exception)
        if settings.DEBUG:
            return None  # let Django's built-in debug page handle it
        return render(
            request,
            "core/500.html",
            {"message": "Something went wrong while processing your request."},
            status=500,
        )
