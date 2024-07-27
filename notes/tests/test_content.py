from django.conf import settings
from django.test import TestCase

from news.models import News


class TestHomePage(TestCase):
    @classmethod
    def setUpTestData(cls):
        all_news = []
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
            news = News(title=f'Новость {index}', text='Просто текст.')
            all_news.append(news)
        News.objects.bulk_create(all_news)
