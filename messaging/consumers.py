import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_username = self.scope['url_route']['kwargs']['room_name']
        self.user = self.scope['user']
        self.room_name = self.get_room_name(self.user.username, self.other_username)
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Notify that user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'username': self.user.username,
                'status': 'online'
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'username': self.user.username,
                'status': 'offline'
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'chat_message':
            message = data.get('message')
            receiver = await self.get_user(self.other_username)

            chat_message = await self.create_message(self.user, receiver, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.user.username,
                    'message_id': chat_message.id,
                    'timestamp': chat_message.created_at.strftime('%b %d, %H:%M'),
                }
            )

        elif message_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing',
                    'username': self.user.username
                }
            )

        elif message_type == 'seen':
            await self.mark_seen(self.user, self.other_username)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'seen',
                    'seen_by': self.user.username
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp'],
        }))

    async def typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': event['username']
        }))

    async def seen(self, event):
        await self.send(text_data=json.dumps({
            'type': 'seen',
            'seen_by': event['seen_by']
        }))

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'status',
            'username': event['username'],
            'status': event['status']
        }))

    @database_sync_to_async
    def create_message(self, sender, receiver, message):
        return ChatMessage.objects.create(sender=sender, receiver=receiver, content=message)

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def mark_seen(self, seen_by, from_user):
        messages = ChatMessage.objects.filter(sender__username=from_user, receiver=seen_by, seen=False)
        messages.update(seen=True)

    def get_room_name(self, u1, u2):
        return '__'.join(sorted([u1, u2]))
