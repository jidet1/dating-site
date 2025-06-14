from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Swipe(models.Model):
    SWIPE_CHOICES = [
        ('like', 'Like'),
        ('pass', 'Pass'),
        ('super_like', 'Super Like'),
    ]
    
    user = models.ForeignKey(User, related_name='swipes_made', on_delete=models.CASCADE)
    target_user = models.ForeignKey(User, related_name='swipes_received', on_delete=models.CASCADE)
    swipe_type = models.CharField(max_length=10, choices=SWIPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'target_user']

    def __str__(self):
        return f"{self.user.first_name} {self.swipe_type}d {self.target_user.first_name}"

class Match(models.Model):
    user1 = models.ForeignKey(User, related_name='matches_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='matches_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user1', 'user2']

    def __str__(self):
        return f"Match: {self.user1.first_name} & {self.user2.first_name}"

    def get_other_user(self, current_user):
        """Get the other user in the match"""
        return self.user2 if self.user1 == current_user else self.user1

class MatchPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    min_age = models.IntegerField(default=18, validators=[MinValueValidator(18), MaxValueValidator(100)])
    max_age = models.IntegerField(default=50, validators=[MinValueValidator(18), MaxValueValidator(100)])
    max_distance = models.IntegerField(default=50, help_text="Maximum distance in km")
    show_me = models.CharField(max_length=1, choices=[('M', 'Men'), ('F', 'Women'), ('B', 'Both')], default='B')
    
    def __str__(self):
        return f"{self.user.first_name}'s preferences"
