from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from django.db.models.signals import post_save

        from accounts.models import RoomMessage
        from accounts.handlers import answer_to_customer_message

        post_save.connect(answer_to_customer_message, sender=RoomMessage)