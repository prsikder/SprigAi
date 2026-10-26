from rest_framework import serializers

from .models import DiseasePredictionHistory


class DiseasePredictionHistorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = DiseasePredictionHistory
        fields = [
            "id",
            "image_url",
            "predicted_disease",
            "confidence",
            "top_predictions",
            "created_at",
        ]
        read_only_fields = fields

    def get_image_url(self, obj):
        request = self.context.get("request")
        if not obj.uploaded_image:
            return ""
        url = obj.uploaded_image.url
        return request.build_absolute_uri(url) if request else url
