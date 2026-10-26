from django import forms


class SoilImageUploadForm(forms.Form):
    image = forms.ImageField(
        label="Upload a soil photo",
        widget=forms.ClearableFileInput(attrs={"accept": "image/jpeg,image/png,image/webp", "data-preview": "#imagePreview"}),
    )
