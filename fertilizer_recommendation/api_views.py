from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import FertilizerRecommendationForm
from .services.fertilizer_service import predict_fertilizer


class FertilizerRecommendationAPIView(APIView):
    """POST /fertilizer-recommendation/api/predict/"""

    def post(self, request):
        form = FertilizerRecommendationForm(request.data)
        if not form.is_valid():
            return Response({"success": False, "errors": form.errors}, status=400)
        d = form.cleaned_data
        result = predict_fertilizer(
            soil_type=d["soil_type"], soil_ph=d["soil_ph"],
            nitrogen_level=d["nitrogen_level"], phosphorus_level=d["phosphorus_level"],
            potassium_level=d["potassium_level"], temperature=d["temperature"],
            humidity=d["humidity"], crop_type=d["crop_type"],
            crop_growth_stage=d["crop_growth_stage"], season=d["season"],
            irrigation_type=d["irrigation_type"], previous_crop=d["previous_crop"],
        )
        status_code = 200 if result["success"] else 503
        return Response(result, status=status_code)
