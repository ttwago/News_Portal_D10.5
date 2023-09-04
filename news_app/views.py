from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import NewsForm
from .models import News, Subscriber
from celery import shared_task


@shared_task
def send_notification_email(subscriber_email, news_title):
    subject = 'Новая новость: {}'.format(news_title)
    message = 'Появилась новая новость: {}'.format(news_title)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [subscriber_email]
    send_mail(subject, message, from_email, recipient_list)


def news_list(request):
    news = News.objects.all()
    return render(request, 'news_list.html', {'news': news})


@shared_task
def create_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save()
            subscribers = Subscriber.objects.all()
            for subscriber in subscribers:
                send_notification_email.delay(subscriber.email, news.title)
            return redirect('news_list')
    else:
        form = NewsForm()
    return render(request, 'create_news.html', {'form': form})
