from rest_framework import serializers

from .models import FertilizerPredictionHistory


class FertilizerPredictionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FertilizerPredictionHistory
        fields = [
            "id",
            "input_data",
            "recommended_fertilizer",
            "created_at",
        ]
        read_only_fields = fields
