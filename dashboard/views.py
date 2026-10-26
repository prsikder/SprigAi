from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from chatbot.models import ChatConversation
from contact.models import ContactMessage
from crop_recommendation.models import CropPredictionHistory
from disease_detection.models import DiseasePredictionHistory
from fertilizer_recommendation.models import FertilizerPredictionHistory
from soil_classification.models import SoilPredictionHistory


def _is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
def home(request):
    user = request.user
    crop_qs = CropPredictionHistory.objects.filter(user=user)
    fert_qs = FertilizerPredictionHistory.objects.filter(user=user)
    disease_qs = DiseasePredictionHistory.objects.filter(user=user)
    soil_qs = SoilPredictionHistory.objects.filter(user=user)

    total_predictions = crop_qs.count() + fert_qs.count() + disease_qs.count() + soil_qs.count()

    recent = []
    for r in crop_qs[:5]:
        recent.append({"type": "Crop", "icon": "bi-flower2", "label": r.predicted_crop, "date": r.created_at, "url": "crop_recommendation:result", "pk": r.pk})
    for r in fert_qs[:5]:
        recent.append({"type": "Fertilizer", "icon": "bi-droplet-half", "label": r.recommended_fertilizer, "date": r.created_at, "url": "fertilizer_recommendation:result", "pk": r.pk})
    for r in disease_qs[:5]:
        recent.append({"type": "Disease", "icon": "bi-bug", "label": r.predicted_disease, "date": r.created_at, "url": "disease_detection:result", "pk": r.pk})
    for r in soil_qs[:5]:
        recent.append({"type": "Soil", "icon": "bi-map", "label": r.predicted_soil, "date": r.created_at, "url": "soil_classification:result", "pk": r.pk})
    recent.sort(key=lambda x: x["date"], reverse=True)
    recent = recent[:8]

    context = {
        "total_predictions": total_predictions,
        "crop_count": crop_qs.count(),
        "fert_count": fert_qs.count(),
        "disease_count": disease_qs.count(),
        "soil_count": soil_qs.count(),
        "recent": recent,
    }
    return render(request, "dashboard/user_dashboard.html", context)


@user_passes_test(_is_admin, login_url="accounts:admin_login")
def admin_home(request):
    total_users = User.objects.count()
    total_crop = CropPredictionHistory.objects.count()
    total_fert = FertilizerPredictionHistory.objects.count()
    total_disease = DiseasePredictionHistory.objects.count()
    total_soil = SoilPredictionHistory.objects.count()
    total_contact = ContactMessage.objects.count()
    total_chats = ChatConversation.objects.count()

    context = {
        "total_users": total_users,
        "total_crop": total_crop,
        "total_fert": total_fert,
        "total_disease": total_disease,
        "total_soil": total_soil,
        "total_contact": total_contact,
        "total_chats": total_chats,
        "total_predictions": total_crop + total_fert + total_disease + total_soil,
        "recent_crop": CropPredictionHistory.objects.select_related("user")[:5],
        "recent_fert": FertilizerPredictionHistory.objects.select_related("user")[:5],
        "recent_disease": DiseasePredictionHistory.objects.select_related("user")[:5],
        "recent_soil": SoilPredictionHistory.objects.select_related("user")[:5],
        "recent_contacts": ContactMessage.objects.all()[:6],
        "chart_labels": ["Crop", "Fertilizer", "Disease", "Soil"],
        "chart_values": [total_crop, total_fert, total_disease, total_soil],
    }
    return render(request, "dashboard/admin_dashboard.html", context)


@user_passes_test(_is_admin, login_url="accounts:admin_login")
def admin_users(request):
    users = User.objects.all().order_by("-created_at")
    return render(request, "dashboard/admin_users.html", {"users": users})


@user_passes_test(_is_admin, login_url="accounts:admin_login")
def admin_contact_messages(request):
    contacts = ContactMessage.objects.all()
    return render(request, "dashboard/admin_contacts.html", {"contacts": contacts})


@user_passes_test(_is_admin, login_url="accounts:admin_login")
def admin_update_contact_status(request, pk):
    contact = get_object_or_404(ContactMessage, pk=pk)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(ContactMessage.Status.choices):
            contact.status = new_status
            contact.save(update_fields=["status"])
            messages.success(request, "Contact message status updated.")
    return redirect("dashboard:admin_contacts")
