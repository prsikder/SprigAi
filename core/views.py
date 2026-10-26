from django.shortcuts import render

BD_DISTRICT_COUNT = 64


def landing(request):
    context = {
        "nav_mode": "hero",
        "district_count": BD_DISTRICT_COUNT,
        "features": [
            {
                "title": "Crop Recommendation",
                "icon": "bi-flower2",
                "desc": "Get the best crop suggestion for your area, district, season and weather.",
                "url_name": "crop_recommendation:form",
            },
            {
                "title": "Fertilizer Recommendation",
                "icon": "bi-droplet-half",
                "desc": "Find the right fertilizer based on soil, crop and growth stage.",
                "url_name": "fertilizer_recommendation:form",
            },
            {
                "title": "Crop Disease Detection",
                "icon": "bi-bug",
                "desc": "Upload a leaf photo and detect crop disease instantly using AI.",
                "url_name": "disease_detection:form",
            },
            {
                "title": "Soil Classification",
                "icon": "bi-map",
                "desc": "Upload a soil photo to identify soil type and suitable crops.",
                "url_name": "soil_classification:form",
            },
            {
                "title": "Farmer AI Chatbot",
                "icon": "bi-chat-dots",
                "desc": "Ask farming questions in plain language, any time.",
                "url_name": "chatbot:chat",
            },
        ],
    }
    return render(request, "core/landing.html", context)


def about(request):
    return render(request, "core/about.html")


def features(request):
    return render(request, "core/features.html")


def faq(request):
    return render(request, "core/faq.html")


def error_404(request, exception=None):
    return render(request, "core/404.html", status=404)


def error_500(request):
    return render(request, "core/500.html", {"message": "Something went wrong on our end."}, status=500)
