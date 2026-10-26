import logging

from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactMessageForm

logger = logging.getLogger("sprigai")


def contact_view(request):
    if request.method == "POST":
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
                return redirect("contact:contact")
            except Exception:
                logger.exception("Failed to save contact message")
                messages.error(request, "We couldn't send your message right now. Please try again.")
    else:
        form = ContactMessageForm()
    return render(request, "contact/contact.html", {"form": form})
