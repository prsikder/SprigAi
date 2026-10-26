SOIL_TYPES = ["Sandy", "Silt", "Loamy", "Clay"]
CROP_TYPES = ["Wheat", "Tomato", "Rice", "Sugarcane", "Potato", "Maize", "Cotton"]
GROWTH_STAGES = ["Harvest", "Vegetative", "Flowering", "Sowing"]
SEASONS = ["Kharif", "Rabi", "Zaid"]  # "Zahid" spelling is normalized to "Zaid" for training consistency
IRRIGATION_TYPES = ["Sprinkler", "Rainfed", "Drip", "Canal"]

# Safe default values used when a user leaves NPK fields blank.
# These represent a moderate, commonly-used baseline (mg/kg) and are easy
# to tune here if you have dataset-specific medians available.
DEFAULT_NITROGEN = 40.0
DEFAULT_PHOSPHORUS = 40.0
DEFAULT_POTASSIUM = 40.0

SOIL_TYPE_CHOICES = [(v, v) for v in SOIL_TYPES]
CROP_TYPE_CHOICES = [(v, v) for v in CROP_TYPES]
GROWTH_STAGE_CHOICES = [(v, v) for v in GROWTH_STAGES]
SEASON_CHOICES = [(v, v) for v in SEASONS]
IRRIGATION_TYPE_CHOICES = [(v, v) for v in IRRIGATION_TYPES]
