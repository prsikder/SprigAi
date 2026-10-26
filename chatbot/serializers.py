from rest_framework import serializers

from .models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_display = serializers.CharField(source="get_sender_display", read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "sender", "sender_display", "message", "metadata", "created_at"]
        read_only_fields = fields
