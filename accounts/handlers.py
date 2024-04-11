from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.utils import timezone

from accounts.services import get_gpt_analyze
from accounts.models import RoomMessage


def answer_to_customer_message(sender, instance: RoomMessage, created, **kwargs):
    pass
    # if created:
    #     message = instance.body
    #     gpt_analyze = get_gpt_analyze(message=message)
        
    #     channel_layer = get_channel_layer()
    #     async_to_sync(channel_layer.group_send)(
    #         f'chat_{instance.author_id}',
    #         {
    #             'type': 'chat_message',
    #             'message': gpt_analyze,
    #             'username': settings.ASISTANT_NAME,
    #             'created_at': timezone.now().strftime('%d.%m.%Y %H:%M')
    #         }
    #     )

    #     instance.response_body = gpt_analyze
    #     instance.save(update_fields=['response_body'])

