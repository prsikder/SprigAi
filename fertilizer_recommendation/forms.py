from django import forms

from .constants import (
    CROP_TYPE_CHOICES,
    GROWTH_STAGE_CHOICES,
    IRRIGATION_TYPE_CHOICES,
    SEASON_CHOICES,
    SOIL_TYPE_CHOICES,
)


class FertilizerRecommendationForm(forms.Form):
    soil_type = forms.ChoiceField(choices=[("", "Select soil type")] + SOIL_TYPE_CHOICES)
    soil_ph = forms.FloatField(
        min_value=0, max_value=14,
        widget=forms.NumberInput(attrs={"step": "0.1", "placeholder": "e.g. 6.5"}),
        label="Soil pH",
    )
    nitrogen_level = forms.FloatField(required=False, min_value=0, max_value=500,
                                       widget=forms.NumberInput(attrs={"step": "0.1", "placeholder": "Optional"}),
                                       label="Nitrogen Level (optional)")
    phosphorus_level = forms.FloatField(required=False, min_value=0, max_value=500,
                                         widget=forms.NumberInput(attrs={"step": "0.1", "placeholder": "Optional"}),
                                         label="Phosphorus Level (optional)")
    potassium_level = forms.FloatField(required=False, min_value=0, max_value=500,
                                        widget=forms.NumberInput(attrs={"step": "0.1", "placeholder": "Optional"}),
                                        label="Potassium Level (optional)")
    temperature = forms.FloatField(min_value=-10, max_value=60,
                                    widget=forms.NumberInput(attrs={"step": "0.1", "placeholder": "e.g. 28"}))
    humidity = forms.FloatField(min_value=0, max_value=100,
                                 widget=forms.NumberInput(attrs={"step": "0.1", "placeholder": "e.g. 65"}))
    crop_type = forms.ChoiceField(choices=[("", "Select crop")] + CROP_TYPE_CHOICES)
    crop_growth_stage = forms.ChoiceField(choices=[("", "Select stage")] + GROWTH_STAGE_CHOICES)
    season = forms.ChoiceField(choices=[("", "Select season")] + SEASON_CHOICES)
    irrigation_type = forms.ChoiceField(choices=[("", "Select irrigation type")] + IRRIGATION_TYPE_CHOICES)
    previous_crop = forms.ChoiceField(choices=[("", "Select previous crop")] + CROP_TYPE_CHOICES)
