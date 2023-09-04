from datetime import timedelta
from celery import shared_task, Celery
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from celery.schedules import crontab
from .models import News, Subscriber

app = Celery('news_project')
app.config_from_object('django.conf:settings', namespace='CELERY')


@shared_task
def send_notification_email(subscriber_email, news_title):
    subject = 'Новая новость: {}'.format(news_title)
    message = 'Появилась новая новость: {}'.format(news_title)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [subscriber_email]
    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_weekly_newsletter():
    now = timezone.now()
    last_week = now - timedelta(days=7)
    news_last_week = News.objects.filter(pub_date__gte=last_week)
    subscribers = Subscriber.objects.all()
    for subscriber in subscribers:
        subscriber_email = subscriber.email
        subject = 'Еженедельная рассылка новостей'
        message = 'Последние новости за неделю:\n\n'
        for news in news_last_week:
            message += '- {}\n'.format(news.title)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [subscriber_email]
        send_mail(subject, message, from_email, recipient_list)


app.conf.beat_schedule = {
    'send-weekly-newsletter': {
        'task': 'news_app.tasks.send_weekly_newsletter',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),
    },
}
