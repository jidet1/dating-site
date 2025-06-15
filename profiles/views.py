from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.db.models import Q, Exists, OuterRef
from django.contrib.auth import get_user_model
from .models import Profile, ProfilePhoto, Interest, BlockedUser, ReportUser
from .forms import ProfileForm, PhotoUploadForm, ReportUserForm
from matching.models import Swipe, MatchPreference
import random

User = get_user_model()

class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'profiles/dashboard.html'
    context_object_name = 'recent_profiles'
    
    def get_queryset(self):
        current_user = self.request.user
        swiped_users = Swipe.objects.filter(user=current_user).values_list('target_user', flat=True)
        blocked_users = BlockedUser.objects.filter(blocker=current_user).values_list('blocked', flat=True)
        queryset = Profile.objects.filter(is_active=True).exclude(user=current_user)
        queryset = queryset.exclude(user__in=swiped_users).exclude(user__in=blocked_users)
        return queryset.order_by('?')[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            profile = self.request.user.profile
            context['has_profile'] = True
            context['profile'] = profile
        except Profile.DoesNotExist:
            context['has_profile'] = False
        return context

class CreateProfileView(LoginRequiredMixin, CreateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/create_profile.html'
    success_url = reverse_lazy('profiles:dashboard')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Profile created successfully!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['interests'] = Interest.objects.all()
        return context

class EditProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/edit_profile.html'
    success_url = reverse_lazy('profiles:dashboard')
    
    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully!')
        return response

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profiles/profile_detail.html'
    context_object_name = 'profile'
    
    def get_object(self):
        user_id = self.kwargs['user_id']
        return get_object_or_404(Profile, user_id=user_id, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = context['profile']
        context['has_swiped'] = Swipe.objects.filter(
            user=self.request.user, 
            target_user=profile.user
        ).exists()
        context['is_blocked'] = BlockedUser.objects.filter(
            blocker=self.request.user,
            blocked=profile.user
        ).exists()
        return context

class DiscoverView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'profiles/discover.html'
    context_object_name = 'profiles'
    paginate_by = 10
    
    def get_queryset(self):
        current_user = self.request.user
        try:
            preferences = MatchPreference.objects.get(user=current_user)
        except MatchPreference.DoesNotExist:
            preferences = None
        swiped_users = Swipe.objects.filter(user=current_user).values_list('target_user', flat=True)
        blocked_users = BlockedUser.objects.filter(blocker=current_user).values_list('blocked', flat=True)
        queryset = Profile.objects.filter(is_active=True).exclude(user=current_user)
        if preferences:
            queryset = queryset.filter(user__date_of_birth__year__lte=2023 - preferences.min_age)
            queryset = queryset.filter(user__date_of_birth__year__gte=2023 - preferences.max_age)
            if preferences.show_me != 'B':
                queryset = queryset.filter(gender=preferences.show_me)
        queryset = queryset.exclude(user__in=swiped_users).exclude(user__in=blocked_users)
        return queryset.order_by('?')

class PhotoUploadView(LoginRequiredMixin, CreateView):
    model = ProfilePhoto
    form_class = PhotoUploadForm
    template_name = 'profiles/photo_upload.html'
    success_url = reverse_lazy('profiles:dashboard')
    
    def form_valid(self, form):
        profile = get_object_or_404(Profile, user=self.request.user)
        form.instance.profile = profile
        if not profile.photos.filter(is_primary=True).exists():
            form.instance.is_primary = True
        response = super().form_valid(form)
        messages.success(self.request, 'Photo uploaded successfully!')
        return response

class PhotoDeleteView(LoginRequiredMixin, View):
    def post(self, request, photo_id):
        photo = get_object_or_404(ProfilePhoto, id=photo_id, profile__user=request.user)
        photo.delete()
        messages.success(request, 'Photo deleted successfully!')
        return redirect('profiles:dashboard')

class BlockUserView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        user_to_block = get_object_or_404(User, id=user_id)
        BlockedUser.objects.get_or_create(
            blocker=request.user,
            blocked=user_to_block
        )
        messages.success(request, 'User blocked successfully!')
        return redirect('profiles:discover')

class ReportUserView(LoginRequiredMixin, CreateView):
    model = ReportUser
    form_class = ReportUserForm
    template_name = 'profiles/report_user.html'
    success_url = reverse_lazy('profiles:discover')
    
    def form_valid(self, form):
        form.instance.reporter = self.request.user
        form.instance.reported = get_object_or_404(User, id=self.kwargs['user_id'])
        response = super().form_valid(form)
        messages.success(self.request, 'Report submitted successfully!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reported_user'] = get_object_or_404(User, id=self.kwargs['user_id'])
        return context