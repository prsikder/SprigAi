from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CropRecommendationForm
from .services.crop_service import predict_crop


class CropRecommendationAPIView(APIView):
    """
    POST /crop-recommendation/api/predict/
    Body: {area, district, season, current_temp, current_humidity, growing_time}
    Requires authentication (session).
    """

    def post(self, request):
        form = CropRecommendationForm(request.data)
        if not form.is_valid():
            return Response({"success": False, "errors": form.errors}, status=400)
        data = form.cleaned_data
        result = predict_crop(
            area=data["area"], district=data["district"], season=data["season"],
            current_temp=data["current_temp"], current_humidity=data["current_humidity"],
            growing_time=data["growing_time"],
        )
        status_code = 200 if result["success"] else 503
        return Response(result, status=status_code)
