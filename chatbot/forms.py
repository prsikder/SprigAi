from django import forms


class ChatMessageForm(forms.Form):
    message = forms.CharField(
        label="Ask SprigAI",
        max_length=1200,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ask about crops, fertilizer, soil, disease, irrigation, seasons, or farm planning...",
            }
        ),
    )

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 3:
            raise forms.ValidationError("Please enter a little more detail so SprigAI can help.")
        return message
