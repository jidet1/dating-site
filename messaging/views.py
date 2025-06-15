from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Conversation, Message
from matching.models import Match
from datetime import datetime

User = get_user_model()

class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'messaging/conversation_list.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        # Only conversations involving current user
        return Conversation.objects.filter(
            match__user1=self.request.user
        ) | Conversation.objects.filter(
            match__user2=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        enriched_conversations = []

        for conversation in context['conversations']:
            match = conversation.match
            other_user = match.user2 if match.user1 == user else match.user1
            last_message = conversation.messages.order_by('-created_at').first()
            unread_count = conversation.messages.filter(is_read=False).exclude(sender=user).count()

            enriched_conversations.append({
                'conversation': conversation,
                'other_user': other_user,
                'last_message': last_message,
                'unread_count': unread_count,
                'last_message_time': last_message.created_at if last_message else None
            })

        # ✅ Fix: Sort using datetime.min instead of integer 0
        from django.utils import timezone

        aware_min = timezone.make_aware(datetime.min)

        enriched_conversations.sort(
            key=lambda x: x['last_message_time'] or aware_min,
            reverse=True
        )


        context['conversations'] = enriched_conversations
        context['user'] = user
        return context
class ConversationDetailView(LoginRequiredMixin, DetailView):
    model = Conversation
    template_name = 'messaging/conversation_detail.html'
    context_object_name = 'conversation'
    
    def get_object(self):
        match_id = self.kwargs['match_id']
        match = get_object_or_404(Match, id=match_id)
        
        # Ensure user is part of this match
        if self.request.user not in [match.user1, match.user2]:
            raise Http404("Conversation not found")
        
        conversation, created = Conversation.objects.get_or_create(match=match)
        
        # Mark messages as read
        Message.objects.filter(
            conversation=conversation
        ).exclude(sender=self.request.user).update(is_read=True)
        
        return conversation
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = self.object.messages.all()
        context['other_user'] = self.object.match.get_other_user(self.request.user)
        return context

class SendMessageView(LoginRequiredMixin, View):
    def post(self, request):
        conversation_id = request.POST.get('conversation_id')
        content = request.POST.get('content')
        
        if not content or not conversation_id:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'})
        
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Check if user is part of this conversation
        if request.user not in [conversation.match.user1, conversation.match.user2]:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'})
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Update conversation timestamp
        conversation.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Message sent',
            'message_id': message.id,
            'content': message.content,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })

from django.http import Http404

