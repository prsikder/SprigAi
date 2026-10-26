"""
Dropdown option lists for Crop Recommendation.

IMPORTANT: These values are copied *exactly* (character-for-character) from
the label encoder classes shipped in ai_models/crop_recommendation/*.pkl so
that user selections always match a category the model was trained on.
Do not "clean up" the raw values below without re-checking the encoders,
or predictions will fall back to the nearest-match safety net unnecessarily.
"""

DISTRICTS = [
    "Bagerhat", "Bandarban", "Barguna", "Barishal", "Bhola", "Bogura", "Brahmanbaria",
    "Chandpur", "Chapai Nawabganj", "Chattogram", "Chuadanga", "CoxsBazar", "Cumilla",
    "Dhaka", "Dinajpur", "Faridpur", "Feni", "Gaibandha", "Gazipur", "Gopalganj",
    "Habiganj", "Jamalpur", "Jashore", "Jhallokati", "Jhenaidah", "Joypurhat",
    "Khagrachari", "Khulna", "Kishoreganj", "Kurigram", "Kushtia", "Lakshmipur",
    "Lalmonirhat", "Madaripur", "Magura", "Manikganj", "Meherpur", "Moulvibazar",
    "Munshiganj", "Mymensingh", "Naogaon", "Narail", "Narayanganj", "Narsingdi",
    "Natore", "Netrokona", "Nilphamari", "Noakhali", "Pabna", "Panchagar",
    "Patuakhali", "Pirojpur", "Rajbari", "Rajshahi", "Rangamati", "Rangpur",
    "Satkhira", "Shariatpur", "Sherpur", "Sirajganj", "Sunamganj", "Sylhet",
    "Tangail", "Thakurgaon",
]

SEASONS = ["Kharif 1", "Kharif 2", "Rabi"]

GROWING_TIME_OPTIONS = [
    "April to Aug", "April to July", "April to May", "April to july", "Aug to Jan",
    "Dec to Feb", "Dec to Jan", "Dec to March", "Jan  to  March", "Jan to Jan",
    "July to  Oct", "July to August", "July to Nov", "June to August",
    "March to April", "March to July", "March to May", "May to July", "May to June",
    "May to Sep", "No need to do", "Nov  to  Feb", "Nov to Aug", "Nov to Feb",
    "Nov to Jan", "Nov to March", "Oct to Dec", "Oct to Jan", "Oct to Nov",
    "Sep to Jan", "Sep to May", "Sep to Oct",
]

# A handful of source dataset labels contain corrupted / mojibake characters.
# We fix them only for *display* purposes; the raw encoder value is still
# what gets fed into the model.
DISPLAY_NAME_FIXES = {
    "Lady\u95f3\u30e6\u7378 Finger": "Lady's Finger (Okra)",
}


def clean_label(value: str) -> str:
    """Collapse duplicate internal whitespace for a nicer dropdown label."""
    return " ".join(value.split())


def display_name(value: str) -> str:
    return DISPLAY_NAME_FIXES.get(value, value)


DISTRICT_CHOICES = [(d, d) for d in DISTRICTS]
SEASON_CHOICES = [(s, s) for s in SEASONS]
GROWING_TIME_CHOICES = [(g, clean_label(g)) for g in GROWING_TIME_OPTIONS]
