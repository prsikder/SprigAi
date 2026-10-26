import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CropRecommendationForm
from .models import CropPredictionHistory
from .services.crop_service import predict_crop

logger = logging.getLogger("sprigai")


@login_required
def crop_form_view(request):
    if request.method == "POST":
        form = CropRecommendationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            result = predict_crop(
                area=data["area"],
                district=data["district"],
                season=data["season"],
                current_temp=data["current_temp"],
                current_humidity=data["current_humidity"],
                growing_time=data["growing_time"],
            )
            if not result["success"]:
                messages.error(request, result["error"])
                return render(request, "crop_recommendation/form.html", {"form": form})

            if result["used_fallback"]:
                messages.warning(request, "One or more inputs weren't an exact match to our training data, so we used the closest known category.")

            record = CropPredictionHistory.objects.create(
                user=request.user,
                area=data["area"], district=data["district"], season=data["season"],
                current_temp=data["current_temp"], current_humidity=data["current_humidity"],
                growing_time=data["growing_time"],
                predicted_crop=result["crop"], predicted_harvest=result["harvest"],
                production=result["production"], suitable_temperature=result["suitable_temperature"],
                suitable_humidity=result["suitable_humidity"], used_fallback=result["used_fallback"],
            )
            return redirect("crop_recommendation:result", pk=record.pk)
    else:
        form = CropRecommendationForm()
    return render(request, "crop_recommendation/form.html", {"form": form})


@login_required
def crop_result_view(request, pk):
    record = get_object_or_404(CropPredictionHistory, pk=pk, user=request.user)
    return render(request, "crop_recommendation/result.html", {"record": record})


@login_required
def crop_history_view(request):
    qs = CropPredictionHistory.objects.filter(user=request.user)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(predicted_crop__icontains=q)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "crop_recommendation/history.html", {"page_obj": page_obj, "q": q})
