from __future__ import division
from future.utils import raise_from

import math
import time
from datetime import datetime
from operator import itemgetter

from pocket import (
    Pocket,
    PocketException,
    PocketAutException
)

from progress.spinner import Spinner

from .config import Configs
from .exceptions import AppException, AppNotConfigured
from .storage import Storage


class PocketApp:
    DEFAULT_WORDS_PER_MINUTE = 180
    REDIRECT_URL = 'http://www.google.com'

    def __init__(self):
        self._configs = Configs()
        self._storage = Storage()

        self._pocket = Pocket(
            self._configs.get('consumer_key'),
            self._configs.get('access_token')
        )

    def configure(self, consumer_key, access_token,
                  words_per_minute, sort_field):
        self._configs.set('consumer_key', consumer_key)
        self._configs.set('access_token', access_token)
        self._configs.set('words_per_minute', words_per_minute)
        self._configs.set('sort_field', sort_field)
        self._configs.set('last_fetch', 0)
        self._configs.write()

        self._storage.clear()

        self._pocket = Pocket(
            consumer_key,
            access_token
        )

    def init_consumer_key(self, consumer_key):
        self._pocket = Pocket(consumer_key)

    def get_request_token(self):
        return self._pocket.get_request_token(
            self.REDIRECT_URL
        )

    def get_access_token(self, request_token):
        return self._pocket.get_access_token(
            request_token
        )

    def add_article(self, url, title=None, tags=None):
        if isinstance(tags, tuple):
            tags = ','.join(list(tags))

        try:
            return self._pocket.add(url, title, tags)
        except PocketException as e:
            raise_from(self._check_exception(e), e)

    def get_articles(self, limit=None, order=None):
        if self._storage.is_empty():
            self.fetch_articles(True)

        articles = self._storage.read(limit, order)
        sort_field = self._configs.get('sort_field')
        if not sort_field:
            sort_field = 'reading_time'

        articles = sorted(articles,
                          key=itemgetter(sort_field))
        return articles

    def search(self, search, state, tag, sort):
        try:
            articles = self._pocket.retrieve(search=search,
                                             state=state,
                                             tag=tag,
                                             sort=sort)
            return self._get_articles_index(articles)
        except PocketException as e:
            raise_from(self._check_exception(e), e)

    def archive_article(self, item_id):
        try:
            self._pocket.archive(int(item_id)).commit()
        except PocketException as e:
            raise_from(self._check_exception(e), e)

    def find_article(self, item_id):
        index = self._storage.read()

        for article in index:
            if str(article['id']) == str(item_id):
                return article

        return None

    def fetch_articles(self, output_progress=False):
        spinner = None
        if output_progress:
            spinner = Spinner('Loading articles ')

        articles_index = []

        last_fetch = self._configs.get('last_fetch')

        offset = 0
        count = 20
        while(True):
            try:
                articles = self._pocket.retrieve(
                    state='unread',
                    count=count,
                    offset=offset,
                    since=last_fetch
                )
            except PocketException as e:
                spinner.finish()
                raise_from(self._check_exception(e), e)

            if not articles['list']:
                break

            articles_index.extend(self._get_articles_index(articles))

            offset += count
            if spinner:
                spinner.next()

        if spinner:
            spinner.finish()

        sort_field = self._configs.get('sort_field')
        if not sort_field:
            sort_field = 'reading_time'

        articles_index = sorted(articles_index,
                                key=itemgetter(sort_field))
        self._storage.write(articles_index)

        self._configs.set('last_fetch', self._get_timestamp(datetime.now()))
        self._configs.write()

    def _get_articles_index(self, articles):
        wpm = self._configs.get('words_per_minute')
        if not wpm:
            wpm = self.DEFAULT_WORDS_PER_MINUTE
        wpm = int(wpm)

        articles_index = []

        articles_list = articles['list']
        if isinstance(articles_list, list) and len(articles_list) == 0:
            return articles_index

        for article in articles_list.values():
            word_count = int(article.get('word_count', 0))
            if word_count == 0:
                reading_time = -1
            else:
                reading_time = int(math.ceil(word_count / wpm))

            title = article.get('resolved_title', None)
            if not title:
                title = article['given_title']

            url = article.get('resolved_url', None)
            if not url:
                url = article['given_url']

            index = {
                'id': article['item_id'],
                'title': title,
                'url': url,
                'word_count': word_count,
                'reading_time': reading_time
            }

            articles_index.append(index)

        return articles_index

    def _get_timestamp(self, date):
        return int(time.mktime(date.timetuple()))

    def _check_exception(self, e):
        if isinstance(e, PocketAutException):
            raise AppNotConfigured('Application is not configured')

        raise AppException(e.message)
