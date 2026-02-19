import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.other_username = self.scope['url_route']['kwargs']['username']
        self.other_user = await self.get_user(self.other_username)
        
        # Create a unique room name for the two users
        user_ids = sorted([self.user.id, self.other_user.id])
        self.room_name = f'chat_{user_ids[0]}_{user_ids[1]}'
        self.room_group_name = f'chat_group_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Update user status to online
        await self.update_user_status(True)
        await self.broadcast_user_status(True)

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Update user status to offline
            await self.update_user_status(False)
            await self.broadcast_user_status(False)
            
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')

        if message_type == 'chat_message':
            message = data['message']
            # Save to records
            await self.save_message(self.user, self.other_user, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message': message,
                    'sender': self.user.username
                }
            )
        elif message_type == 'typing':
            is_typing = data.get('is_typing', False)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.typing',
                    'is_typing': is_typing,
                    'sender': self.user.username
                }
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender']
        }))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'is_typing': event['is_typing'],
            'sender': event['sender']
        }))

    async def broadcast_user_status(self, is_online):
        # This could be broadcasted to all users or just the current room
        # For simplicity, we broadcast to the current room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user.status',
                'username': self.user.username,
                'is_online': is_online
            }
        )

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'username': event['username'],
            'is_online': event['is_online']
        }))

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def save_message(self, sender, receiver, message):
        return Message.objects.create(sender=sender, receiver=receiver, message=message)

    @database_sync_to_async
    def update_user_status(self, is_online):
        User.objects.filter(id=self.user.id).update(is_online=is_online)
