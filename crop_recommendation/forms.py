from django import forms

from .constants import DISTRICT_CHOICES, GROWING_TIME_CHOICES, SEASON_CHOICES


class CropRecommendationForm(forms.Form):
    area = forms.FloatField(
        min_value=0, max_value=1_000_000,
        widget=forms.NumberInput(attrs={"step": "0.01", "placeholder": "e.g. 2.5"}),
        help_text="Land area in acres/bigha (as used in your records).",
    )
    district = forms.ChoiceField(choices=[("", "Select district")] + DISTRICT_CHOICES)
    season = forms.ChoiceField(choices=[("", "Select season")] + SEASON_CHOICES)
    current_temp = forms.FloatField(
        min_value=-10, max_value=60,
        widget=forms.NumberInput(attrs={"step": "0.1", "placeholder": "e.g. 29.5"}),
        label="Current Temperature (°C)",
    )
    current_humidity = forms.FloatField(
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={"step": "0.1", "placeholder": "e.g. 70"}),
        label="Current Humidity (%)",
    )
    growing_time = forms.ChoiceField(
        choices=[("", "Select growing time")] + GROWING_TIME_CHOICES,
        label="Growing Time",
    )
