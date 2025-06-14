from django.contrib import admin
from .models import Swipe, Match, MatchPreference

@admin.register(Swipe)
class SwipeAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_user', 'swipe_type', 'created_at']
    list_filter = ['swipe_type', 'created_at']
    search_fields = ['user__email', 'target_user__email']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user1__email', 'user2__email']

@admin.register(MatchPreference)
class MatchPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'min_age', 'max_age', 'max_distance', 'show_me']
    search_fields = ['user__email']
