from rest_framework import serializers

from .models import SoilPredictionHistory


class SoilPredictionHistorySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SoilPredictionHistory
        fields = [
            "id",
            "image_url",
            "predicted_soil",
            "confidence",
            "suggested_crops",
            "created_at",
        ]
        read_only_fields = fields

    def get_image_url(self, obj):
        request = self.context.get("request")
        if not obj.image:
            return ""
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url
