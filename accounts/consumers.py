import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone

from accounts.models import RoomMessage
from accounts.services import get_gpt_analyze

# Create a consumer class
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.customer = self.scope['url_route']['kwargs']['customer_id']
        self.room_group_name = f'chat_{self.customer}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        customer_id = data['customer_id']
        created_at = timezone.now().strftime('%d.%m.%Y %H:%M')
        room_id = data['room_id']

        room_message = await self.save_message(customer_id, room_id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'message_id': room_message.pk,
                'username': username,
                'created_at': created_at
            }
        )

        await self.gpt_analyze(customer_id, room_message.pk, message)
        

    @sync_to_async
    def save_message(self, customer_id, room_id, message):
        return RoomMessage.objects.create(author_id=customer_id, room_id=room_id, body=message)

    @sync_to_async
    def gpt_analyze(self, customer_id, message_id, message):
        get_gpt_analyze(customer_id, message_id, message)

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        message_id = event['message_id']
        username = event['username']
        created_at = event['created_at']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'message_id': message_id,
            'username': username,
            'created_at': created_at
        }))

    # Receive message from room group
    async def gpt_answer(self, event):
        message = event['message']
        message_id = event['message_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'answer': message,
            'message_id': message_id
        }))