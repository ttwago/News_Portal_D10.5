from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import News, Subscriber
from .tasks import send_notification_email


@receiver(post_save, sender=News)
def send_notification_on_news_creation(sender, instance, **kwargs):
    subscribers = Subscriber.objects.all()
    for subscriber in subscribers:
        send_notification_email.delay(subscriber.email, instance.title)
