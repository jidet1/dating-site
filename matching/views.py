from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, CreateView
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from .models import Swipe, Match, MatchPreference
from .forms import MatchPreferenceForm
from profiles.models import Profile
from messaging.models import Conversation
from django.db.models import Q

User = get_user_model()

class SwipeView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'matching/swipe.html'
    context_object_name = 'profiles'
    
    def get_queryset(self):
        current_user = self.request.user
        
        # Get users already swiped on
        swiped_users = Swipe.objects.filter(user=current_user).values_list('target_user', flat=True)
        
        # Get available profiles to swipe on
        queryset = Profile.objects.filter(is_active=True).exclude(user=current_user).exclude(user__in=swiped_users)
        
        return queryset.order_by('?')[:1]  # Get one random profile

class LikeUserView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        
        # Create swipe
        swipe, created = Swipe.objects.get_or_create(
            user=request.user,
            target_user=target_user,
            defaults={'swipe_type': 'like'}
        )
        
        # Check if target user has also liked this user
        reverse_swipe = Swipe.objects.filter(
            user=target_user,
            target_user=request.user,
            swipe_type='like'
        ).first()
        
        if reverse_swipe:
            # Create match
            match, created = Match.objects.get_or_create(
                user1=min(request.user, target_user, key=lambda x: x.id),
                user2=max(request.user, target_user, key=lambda x: x.id)
            )
            
            if created:
                # Create conversation
                Conversation.objects.create(match=match)
                return JsonResponse({'status': 'match', 'message': 'It\'s a match!'})
        
        return JsonResponse({'status': 'liked', 'message': 'User liked!'})

class PassUserView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        
        # Create swipe
        swipe, created = Swipe.objects.get_or_create(
            user=request.user,
            target_user=target_user,
            defaults={'swipe_type': 'pass'}
        )
        
        return JsonResponse({'status': 'passed', 'message': 'User passed!'})

class MatchesView(LoginRequiredMixin, ListView):
    model = Match
    template_name = 'matching/matches.html'
    context_object_name = 'matches'
    
    def get_queryset(self):
        user = self.request.user
        return Match.objects.filter(user1=user) | Match.objects.filter(user2=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        for match in context['matches']:
            match.other_user = match.get_other_user(user)
        return context

class PreferencesView(LoginRequiredMixin, UpdateView):
    model = MatchPreference
    form_class = MatchPreferenceForm
    template_name = 'matching/preferences.html'
    success_url = reverse_lazy('profiles:dashboard')
    
    def get_object(self):
        obj, created = MatchPreference.objects.get_or_create(user=self.request.user)
        return obj
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Preferences updated successfully!')
        return response
    
class UnmatchView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        other_user = get_object_or_404(User, id=user_id)
        Match.objects.filter(
            (Q(user1=request.user) & Q(user2=other_user)) |
            (Q(user1=other_user) & Q(user2=request.user))
        ).delete()
        messages.success(request, 'User unmatched successfully!')
        return redirect('profiles:dashboard')
