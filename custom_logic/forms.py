
from django import forms

class ChatInputForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={
        "rows": 2,
        "placeholder": "Ask a question about your business...",
        "class": "w-full p-2 rounded border"
    }))