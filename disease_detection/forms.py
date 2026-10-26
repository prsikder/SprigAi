from django import forms


class DiseaseImageUploadForm(forms.Form):
    image = forms.ImageField(
        label="Upload a crop leaf photo",
        widget=forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "data-preview": "#imagePreview"}),
    )
