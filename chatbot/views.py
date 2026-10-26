import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .models import ChatConversation, ChatMessage
from .services.chatbot_service import get_bot_reply
from .services.env_config import is_chatbot_ready

logger = logging.getLogger("sprigai")


def _get_or_create_conversation(user):
    conversation = ChatConversation.objects.filter(user=user).first()
    if not conversation:
        conversation = ChatConversation.objects.create(user=user, title="Farming Q&A")
    return conversation


@login_required
def chat_view(request):
    conversation = _get_or_create_conversation(request.user)
    messages_qs = conversation.messages.all()
    return render(
        request,
        "chatbot/chat.html",
        {
            "conversation": conversation,
            "chat_messages": messages_qs,
            "chatbot_ready": is_chatbot_ready(),
        },
    )


@login_required
@require_POST
@csrf_protect
def send_message_view(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"success": False, "error": "Invalid request."}, status=400)

    message = (payload.get("message") or "").strip()
    if not message:
        return JsonResponse({"success": False, "error": "Message cannot be empty."}, status=400)
    if len(message) > 2000:
        return JsonResponse({"success": False, "error": "Message is too long (max 2000 characters)."}, status=400)

    conversation = _get_or_create_conversation(request.user)

    history = list(conversation.messages.values("sender", "content").order_by("created_at")[:20])

    ChatMessage.objects.create(conversation=conversation, sender=ChatMessage.Sender.USER, content=message)

    result = get_bot_reply(message, history=history)

    ChatMessage.objects.create(conversation=conversation, sender=ChatMessage.Sender.BOT, content=result["reply"])
    conversation.save(update_fields=["updated_at"])

    return JsonResponse({"success": True, "reply": result["reply"], "provider_ok": result["success"]})


@login_required
@require_POST
def clear_chat_view(request):
    conversation = _get_or_create_conversation(request.user)
    conversation.messages.all().delete()
    return redirect("chatbot:chat")
