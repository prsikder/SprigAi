import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SoilImageUploadForm
from .models import SoilPredictionHistory
from .services.soil_service import predict_soil

logger = logging.getLogger("sprigai")


@login_required
def soil_form_view(request):
    if request.method == "POST":
        form = SoilImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]
            result = predict_soil(image)
            if not result["success"]:
                messages.error(request, result["error"])
                return render(request, "soil_classification/form.html", {"form": form})

            record = SoilPredictionHistory.objects.create(
                user=request.user, image=image,
                predicted_soil=result["predicted_class"], confidence=result["confidence"],
                suggested_crops=result["suggested_crops"], top_predictions=result["top_predictions"],
            )
            return redirect("soil_classification:result", pk=record.pk)
    else:
        form = SoilImageUploadForm()
    return render(request, "soil_classification/form.html", {"form": form})


@login_required
def soil_result_view(request, pk):
    record = get_object_or_404(SoilPredictionHistory, pk=pk, user=request.user)
    return render(request, "soil_classification/result.html", {"record": record})


@login_required
def soil_history_view(request):
    qs = SoilPredictionHistory.objects.filter(user=request.user)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(predicted_soil__icontains=q)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "soil_classification/history.html", {"page_obj": page_obj, "q": q})
