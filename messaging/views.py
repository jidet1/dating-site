from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import JsonResponse, Http404
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.html import escape
from .models import Conversation, Message
from matching.models import Match
from datetime import datetime


User = get_user_model()

class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'messaging/conversation_list.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        return Conversation.objects.filter(
            Q(match__user1=self.request.user) | Q(match__user2=self.request.user)
        ).select_related('match__user1', 'match__user2').prefetch_related('messages')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        enriched_conversations = []

        for conversation in context['conversations']:
            match = conversation.match
            other_user = match.user2 if match.user1 == user else match.user1
            last_message = conversation.messages.all().order_by('-created_at').first()
            unread_count = conversation.messages.all().filter(is_read=False).exclude(sender=user).count()

            enriched_conversations.append({
                'conversation': conversation,
                'other_user': other_user,
                'last_message': last_message,
                'unread_count': unread_count,
                'last_message_time': last_message.created_at if last_message else None
            })

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

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conversation = self.get_object()

        # Use correct related name from ChatMessage
        context['chat_messages'] = conversation.messages.order_by('created_at')
        
        other_user = conversation.participants.exclude(id=self.request.user.id).first()
        context['other_user'] = other_user

        return context
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = self.object.messages.select_related('sender').all()
        match = self.object.match
        if hasattr(match, 'get_other_user'):
            context['other_user'] = match.get_other_user(self.request.user)
        else:
            # Fallback: determine the other user manually
            if self.request.user == match.user1:
                context['other_user'] = match.user2
            elif self.request.user == match.user2:
                context['other_user'] = match.user1
            else:
                raise Http404("Invalid match configuration")
        return context

class SendMessageView(LoginRequiredMixin, View):
    def post(self, request):
        conversation_id = request.POST.get('conversation_id')
        content = request.POST.get('content')
        
        if not content or not conversation_id:
            return JsonResponse({'status': 'error', 'message': 'Content or conversation ID missing'}, status=400)
        
        content = escape(content.strip())[:1000]  # Sanitize and limit to 1000 characters
        
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        if not hasattr(conversation, 'match') or not conversation.match:
            return JsonResponse({'status': 'error', 'message': 'Conversation match not found'}, status=400)

        if request.user not in [conversation.match.user1, conversation.match.user2]:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
        
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )

        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            if channel_layer is not None:
                async_to_sync(channel_layer.group_send)(
                    f"chat_{conversation.id}",
                    {
                        "type": "chat.message",
                        "message": {
                            "id": message.id,
                            "sender": message.sender.username,
                            "content": message.content,
                            "created_at": message.created_at.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    }
                )
        except ImportError:
            pass  # Channels not installed, skip real-time notification
        except Exception as e:
            # Log or handle other exceptions (e.g., channel layer misconfiguration)
            pass

        return JsonResponse({
            'status': 'success',
            'message': 'Message sent',
            'message_id': message.id,
            'content': message.content,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })