import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FertilizerRecommendationForm
from .models import FertilizerPredictionHistory
from .services.fertilizer_service import predict_fertilizer

logger = logging.getLogger("sprigai")


@login_required
def fertilizer_form_view(request):
    if request.method == "POST":
        form = FertilizerRecommendationForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            result = predict_fertilizer(
                soil_type=d["soil_type"], soil_ph=d["soil_ph"],
                nitrogen_level=d["nitrogen_level"], phosphorus_level=d["phosphorus_level"],
                potassium_level=d["potassium_level"], temperature=d["temperature"],
                humidity=d["humidity"], crop_type=d["crop_type"],
                crop_growth_stage=d["crop_growth_stage"], season=d["season"],
                irrigation_type=d["irrigation_type"], previous_crop=d["previous_crop"],
            )
            if not result["success"]:
                messages.error(request, result["error"])
                return render(request, "fertilizer_recommendation/form.html", {"form": form})

            if result["npk_imputed"]:
                messages.info(request, "One or more NPK values were left blank.")

            record = FertilizerPredictionHistory.objects.create(
                user=request.user, soil_type=d["soil_type"], soil_ph=d["soil_ph"],
                nitrogen_level=d["nitrogen_level"], phosphorus_level=d["phosphorus_level"],
                potassium_level=d["potassium_level"], temperature=d["temperature"],
                humidity=d["humidity"], crop_type=d["crop_type"],
                crop_growth_stage=d["crop_growth_stage"], season=d["season"],
                irrigation_type=d["irrigation_type"], previous_crop=d["previous_crop"],
                recommended_fertilizer=result["fertilizer"], npk_imputed=result["npk_imputed"],
            )
            return redirect("fertilizer_recommendation:result", pk=record.pk)
    else:
        form = FertilizerRecommendationForm()
    return render(request, "fertilizer_recommendation/form.html", {"form": form})


@login_required
def fertilizer_result_view(request, pk):
    record = get_object_or_404(FertilizerPredictionHistory, pk=pk, user=request.user)
    return render(request, "fertilizer_recommendation/result.html", {"record": record})


@login_required
def fertilizer_history_view(request):
    qs = FertilizerPredictionHistory.objects.filter(user=request.user)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(recommended_fertilizer__icontains=q)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "fertilizer_recommendation/history.html", {"page_obj": page_obj, "q": q})
