from rest_framework import serializers

from .models import CropPredictionHistory


class CropPredictionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CropPredictionHistory
        fields = [
            "id",
            "input_data",
            "predicted_crop",
            "production",
            "harvest",
            "suitable_temperature",
            "suitable_humidity",
            "created_at",
        ]
        read_only_fields = fields
