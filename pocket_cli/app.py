import math
import time
from datetime import datetime
from operator import itemgetter

from pocket import Pocket
from progress.spinner import Spinner

from .config import Configs
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

    def configure(self, consumer_key, access_token, words_per_minute):
        self._configs.set('consumer_key', consumer_key)
        self._configs.set('access_token', access_token)
        self._configs.set('words_per_minute', words_per_minute)
        self._configs.write()

    def get_request_token(self, consumer_key):
        return self._pocket.get_request_token(
            consumer_key, self.REDIRECT_URL
        )

    def get_access_token(self, consumer_key, request_token):
        return self._pocket.get_access_token(
            consumer_key, request_token
        )

    def add_article(self, url, title=None, tags=None):
        if isinstance(tags, tuple):
            tags = ','.join(list(tags))

        return self._pocket.add(url, title, tags)

    def get_articles(self, limit=None, order=None):
        if self._storage.is_empty():
            self.fetch_articles(True)

        return self._storage.read(limit, order)

    def archive_article(self, item_id):
        self._pocket.archive(int(item_id)).commit()

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

        wpm = self._configs.get('words_per_minute')
        if not wpm:
            wpm = self.DEFAULT_WORDS_PER_MINUTE

        last_fetch = self._configs.get('last_fetch')

        offset = 0
        count = 20
        while(True):
            articles = self._pocket.retrieve(
                state='unread',
                count=count,
                offset=offset,
                since=last_fetch
            )

            if not articles['list']:
                break

            for article in articles['list'].values():
                word_count = int(article['word_count'])
                if word_count == 0:
                    reading_time = -1
                else:
                    reading_time = math.ceil(word_count / wpm)

                title = article['resolved_title']
                if not title:
                    title = article['given_title']

                url = article['resolved_url']
                if not url:
                    url = article['given_url']

                index = {
                    'id': article['item_id'],
                    'title': title,
                    'url': url,
                    'word_count': article['word_count'],
                    'reading_time': reading_time
                }

                articles_index.append(index)

            offset += count
            if spinner:
                spinner.next()

        if spinner:
            spinner.finish()

        articles_index = sorted(articles_index,
                                key=itemgetter('reading_time'))
        self._storage.write(articles_index)

        self._configs.set('last_fetch', self._get_timestamp(datetime.now()))
        self._configs.write()

    def _get_timestamp(self, date):
        return int(time.mktime(date.timetuple()))
