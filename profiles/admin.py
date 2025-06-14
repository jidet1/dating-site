from django.contrib import admin
from .models import Profile, ProfilePhoto, Interest, ProfileInterest, BlockedUser, ReportUser

class ProfilePhotoInline(admin.TabularInline):
    model = ProfilePhoto
    extra = 1

class ProfileInterestInline(admin.TabularInline):
    model = ProfileInterest
    extra = 1

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'age', 'location', 'is_active', 'created_at']
    list_filter = ['gender', 'interested_in', 'is_active', 'is_verified', 'education', 'looking_for']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'location']
    inlines = [ProfilePhotoInline, ProfileInterestInline]
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ['blocker', 'blocked', 'created_at']
    list_filter = ['created_at']
    search_fields = ['blocker__email', 'blocked__email']

@admin.register(ReportUser)
class ReportUserAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reported', 'reason', 'is_resolved', 'created_at']
    list_filter = ['reason', 'is_resolved', 'created_at']
    search_fields = ['reporter__email', 'reported__email']
    actions = ['mark_resolved']
    
    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_resolved.short_description = "Mark selected reports as resolved"
