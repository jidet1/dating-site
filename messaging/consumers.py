# consumers.py

import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Conversation, ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_username = self.scope['url_route']['kwargs']['username']
        self.current_user = self.scope["user"]

        self.other_user = await sync_to_async(User.objects.get)(username=self.other_username)

        self.conversation = await self.get_or_create_conversation(self.current_user, self.other_user)
        self.room_name = f"chat_{self.conversation.id}"
        self.room_group_name = f"chat_{self.conversation.id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('content')
        sender_username = data.get('sender')
        conversation_id = data.get('conversation_id')

        if message_content and sender_username and conversation_id:
            sender = await sync_to_async(User.objects.get)(username=sender_username)
            chat_message = await self.save_message(sender, self.conversation, message_content)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': chat_message.content,
                    'sender': sender.username,
                    'created_at': chat_message.created_at.isoformat(),
                    'message_id': chat_message.id,
                    'is_read': chat_message.is_read,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'created_at': event['created_at'],
            'message_id': event['message_id'],
            'is_read': event['is_read'],
        }))

    @sync_to_async
    def get_or_create_conversation(self, user1, user2):
        conversation = Conversation.objects.filter(participants=user1).filter(participants=user2).first()
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(user1, user2)
        return conversation

    @sync_to_async
    def save_message(self, sender, conversation, content):
        message = ChatMessage.objects.create(
            sender=sender,
            conversation=conversation,
            content=content
        )
        return message
