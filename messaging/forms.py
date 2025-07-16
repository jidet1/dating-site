from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': 'Type your message and use 😊 emojis...',
                'style': 'flex: 1; padding: 0.8rem 1.2rem; border: 2px solid rgba(255,255,255,0.3); border-radius: 25px; background: rgba(255,255,255,0.9); font-size: 16px;',
                'required': True,
                'id': 'messageInput',
            }),
        }