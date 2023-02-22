from time import sleep
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from celery import shared_task
from django.core.mail import send_mail as django_send_mail


@shared_task
def add(x, y):
    sleep(5)
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task
def send_mail(subject, message, from_email):
    django_send_mail(subject, message, from_email, ["admin@example.com"])


@shared_task
def send_mail_to_admin():
    django_send_mail("subject", str(datetime.now()), "noreply@test.com", ["admin@example.com"])


@shared_task
def parse_news():
    r = requests.get("https://news.ycombinator.com/rss")
    soup = BeautifulSoup(r.content, features="xml")
    articles = soup.findAll("item")
    print(soup.find("title").text)  # noqa: F401
    for a in articles:
        print(a.title.text, a.link.text)
    return len(articles)
