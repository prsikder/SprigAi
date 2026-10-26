import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DiseaseImageUploadForm
from .models import DiseasePredictionHistory
from .services.disease_service import predict_disease

logger = logging.getLogger("sprigai")


@login_required
def disease_form_view(request):
    if request.method == "POST":
        form = DiseaseImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data["image"]
            result = predict_disease(image)
            if not result["success"]:
                messages.error(request, result["error"])
                return render(request, "disease_detection/form.html", {"form": form})

            record = DiseasePredictionHistory.objects.create(
                user=request.user, image=image,
                predicted_disease=result["predicted_class"], confidence=result["confidence"],
                top_predictions=result["top_predictions"],
            )
            return redirect("disease_detection:result", pk=record.pk)
    else:
        form = DiseaseImageUploadForm()
    return render(request, "disease_detection/form.html", {"form": form})


@login_required
def disease_result_view(request, pk):
    from .services.disease_service import get_advisory, is_healthy_label
    record = get_object_or_404(DiseasePredictionHistory, pk=pk, user=request.user)
    context = {
        "record": record,
        "advisory": get_advisory(record.predicted_disease),
        "is_healthy": is_healthy_label(record.predicted_disease),
    }
    return render(request, "disease_detection/result.html", context)


@login_required
def disease_history_view(request):
    qs = DiseasePredictionHistory.objects.filter(user=request.user)
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(predicted_disease__icontains=q)
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "disease_detection/history.html", {"page_obj": page_obj, "q": q})
