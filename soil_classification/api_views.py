from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .services.soil_service import predict_soil


class SoilClassificationAPIView(APIView):
    """POST /soil-classification/api/predict/  (multipart/form-data, field: image)"""
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        image = request.FILES.get("image")
        if not image:
            return Response({"success": False, "error": "No image file provided."}, status=400)
        result = predict_soil(image)
        status_code = 200 if result["success"] else 503
        return Response(result, status=status_code)
