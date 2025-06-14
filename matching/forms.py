from django import forms
from .models import MatchPreference

class MatchPreferenceForm(forms.ModelForm):
    class Meta:
        model = MatchPreference
        fields = ['min_age', 'max_age', 'max_distance', 'show_me']
        widgets = {
            'min_age': forms.NumberInput(attrs={'min': 18, 'max': 100}),
            'max_age': forms.NumberInput(attrs={'min': 18, 'max': 100}),
            'max_distance': forms.NumberInput(attrs={'min': 1, 'max': 500}),
        }
