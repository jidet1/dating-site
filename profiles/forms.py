from django import forms
from .models import Profile, ProfilePhoto, Interest, ProfileInterest, ReportUser
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileForm(forms.ModelForm):
    interests = forms.ModelMultipleChoiceField(
        queryset=Interest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Profile
        fields = [
            'bio', 'gender', 'interested_in', 'location', 'height', 
            'occupation', 'education', 'looking_for', 'smoking', 'drinking'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'location': forms.TextInput(attrs={'placeholder': 'City, Country'}),
            'height': forms.NumberInput(attrs={'placeholder': 'Height in cm'}),
            'occupation': forms.TextInput(attrs={'placeholder': 'Your job title'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['interests'].initial = self.instance.interests.values_list('interest', flat=True)
    
    def save(self, commit=True):
        profile = super().save(commit)
        if commit:
            # Handle interests
            ProfileInterest.objects.filter(profile=profile).delete()
            for interest in self.cleaned_data['interests']:
                ProfileInterest.objects.create(profile=profile, interest=interest)
        return profile

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = ProfilePhoto
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'accept': 'image/*'})
        }

class ReportUserForm(forms.ModelForm):
    class Meta:
        model = ReportUser
        fields = ['reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Please provide details...'})
        }
