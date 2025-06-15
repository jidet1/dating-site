from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    RELATIONSHIP_CHOICES = [
        ('casual', 'Casual Dating'),
        ('serious', 'Serious Relationship'),
        ('marriage', 'Marriage'),
        ('friendship', 'Friendship'),
    ]
    
    EDUCATION_CHOICES = [
        ('high_school', 'High School'),
        ('bachelors', 'Bachelor\'s Degree'),
        ('masters', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    interested_in = models.CharField(max_length=1, choices=GENDER_CHOICES)
    location = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True, help_text="Height in cm")
    occupation = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES, blank=True)
    looking_for = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, blank=True)
    smoking = models.BooleanField(default=False)
    drinking = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name}'s Profile"

    @property
    def age(self):
        return self.user.age

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_primary_photo(self):
        """Returns the URL of the user's primary profile photo or None if not set."""
        primary = self.photos.filter(is_primary=True).first()
        return primary.image.url if primary else None


class ProfilePhoto(models.Model):
    profile = models.ForeignKey(Profile, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_photos/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.profile.user.first_name}'s Photo"


class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name


class ProfileInterest(models.Model):
    profile = models.ForeignKey(Profile, related_name='interests', on_delete=models.CASCADE)
    interest = models.ForeignKey(Interest, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['profile', 'interest']


class BlockedUser(models.Model):
    blocker = models.ForeignKey(User, related_name='blocked_users', on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocked_by', on_delete=models.CASCADE)
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['blocker', 'blocked']


class ReportUser(models.Model):
    REPORT_REASONS = [
        ('fake', 'Fake Profile'),
        ('inappropriate', 'Inappropriate Content'),
        ('harassment', 'Harassment'),
        ('spam', 'Spam'),
        ('other', 'Other'),
    ]

    reporter = models.ForeignKey(User, related_name='reports_made', on_delete=models.CASCADE)
    reported = models.ForeignKey(User, related_name='reports_received', on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        unique_together = ['reporter', 'reported']
