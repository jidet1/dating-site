import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Conversation, Message
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.other_username = self.scope['url_route']['kwargs']['username']
        self.user = self.scope['user']
        
        # Check authentication
        if not self.user.is_authenticated:
            await self.close()
            return
            # Prevent users from chatting with themselves
            if self.user.username == self.other_username:
                await self.close()
                return
        # Get conversation
        self.conversation = await self.get_conversation()
        if not self.conversation:
            await self.close()
            return

        self.room_group_name = f'conversation_{self.conversation.id}'

        # Join conversation group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message')
            sender_username = data.get('sender')
            conversation_id = data.get('conversation_id')

            # Validate required fields
            if not all([message, sender_username, conversation_id]):
                await self.send(text_data=json.dumps({'error': 'Missing required fields.'}))
                return

            # Validate sender
            if sender_username != self.user.username:
                await self.send(text_data=json.dumps({'error': 'Sender mismatch.'}))
                return

            # Validate conversation membership
            if not self.conversation or str(self.conversation.id) != str(conversation_id):
                await self.send(text_data=json.dumps({'error': 'Invalid conversation.'}))
                return

            # Save message
            saved_message = await self.save_message(message, sender_username, conversation_id)

            # Only broadcast if message was saved successfully
            if saved_message is not None:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'sender': sender_username,
                        'created_at': saved_message.created_at.strftime('%Y-%m-%dT%H:%M:%S'),
                        'is_read': saved_message.is_read,
                    }
                )
            else:
                await self.send(text_data=json.dumps({'error': 'Failed to save message.'}))
        except Exception as e:
            await self.send(text_data=json.dumps({'error': f'Invalid data: {str(e)}'}))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'created_at': event['created_at'],
            'is_read': event['is_read'],
        }))

    @database_sync_to_async
    def get_conversation(self):
        try:
            other_user = User.objects.get(username=self.other_username)
            conversation = Conversation.objects.filter(
                match__user1=self.user
            ).filter(
                match__user2=other_user
            ).first() or Conversation.objects.filter(
                match__user1=other_user
            ).filter(
                match__user2=self.user
            ).first()

            return conversation
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, message, sender_username, conversation_id):
        try:
            sender = User.objects.get(username=sender_username)
            conversation = Conversation.objects.get(id=conversation_id)
            return Message.objects.create(
                conversation=conversation,
                sender=sender,
                content=message,
                is_read=False
            )
        except (User.DoesNotExist, Conversation.DoesNotExist):
            return None