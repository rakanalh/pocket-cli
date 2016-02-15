import random
import subprocess
import sys
import webbrowser

import click

from .app import PocketApp
from .exceptions import AppNotConfigured, AppException
from .utils import format_article


pocket_app = PocketApp()

WORDS_PER_MINUTE = 180


@click.group()
def main():
    pass


@click.command()
@click.option('--consumer-key', '-k',
              prompt='Please provide your consumer key')
@click.option('--sort_field', '-s',
              type=click.Choice(['id', 'reading_time']),
              prompt='Please provide your preferred sort field')
@click.option('--words-per-minute', '-wpm',
              type=click.INT,
              prompt='Please prefer your reading speed in words per minute',
              help='Used in calculating reading time for each article')
def configure(consumer_key, sort_field, words_per_minute):
    request_token = pocket_app.get_request_token(consumer_key)

    if not request_token:
        print('Could not obtain request_token')
        return

    url = 'http://getpocket.com/auth/authorize?request_token={0}' \
          '&redirect_uri={1}'.format(request_token, 'http://www.google.com')

    print('You will have to authorize the application to access your articles')
    print('Enter any key once you\'re redirected to google.com')
    webbrowser.open_new_tab(url)
    input()

    access_token = pocket_app.get_access_token(consumer_key, request_token)

    if not access_token:
        print('Could not obtain access token')
        return

    pocket_app.configure(consumer_key, access_token,
                         words_per_minute, sort_field)
    print('The application is ready to use')


@click.command(name='add')
@click.option('--url', '-u',
              help='The URL to be added')
@click.option('--title', '-t',
              help='The article\'s title')
@click.option('--tags', '-g', multiple=True,
              help='Tags to be associated. '
                   'Can be multiple tags --tags=tag1, --tags=tag2')
def add_article(url, title, tags):
    response = pocket_app.add_article(url, title, tags)
    if response and response['status'] == 1:
        pocket_app.fetch_articles(False)
        print('URL has been added')


@click.command(name='list')
@click.option('--limit', '-l', default=10,
              help='Number of items to list')
@click.option('--order', '-o', default='asc',
              type=click.Choice(['asc', 'desc']),
              help='Order of items to return')
def list_articles(limit, order):
    try:
        articles = pocket_app.get_articles(limit, order)
    except AppNotConfigured:
        app_not_configured()
        return
    except AppException as e:
        exception_occured(e)
        return

    if not articles:
        print('Articles index is empty,'
              'run pocket-cli fetch to index your articles')
        return

    try:
        pager = subprocess.Popen(['less'],
                                 stdin=subprocess.PIPE,
                                 stdout=sys.stdout)
        for article in articles:
            if int(article['reading_time']) <= 0:
                article['reading_time'] = 'Unknown'
            pager.stdin.write(
                bytearray(format_article(article, line=True), 'utf-8'))

        pager.stdin.close()
        pager.wait()
    except (KeyboardInterrupt, ValueError):
        pass


@click.command()
@click.argument('item_id')
@click.option('--open-origin', '-o', is_flag=True,
              default=False,
              help='Open original URL not the pocket one')
@click.option('--archive', '-a', is_flag=True,
              default=False,
              help='Archive article')
def read(item_id, open_origin, archive):
    article = pocket_app.find_article(item_id)

    if not article:
        print('Article with this ID was not found.')

    url = 'https://getpocket.com/a/read/{}'.format(article['id'])

    print(format_article(article, header='Selected Article'))

    if open_origin:
        url = article['url']

    webbrowser.open_new_tab(url)

    if archive:
        pocket_app.archive_article(article['id'])


@click.command(name='random')
@click.option('--archive', '-a', is_flag=True,
              default=False,
              help='Archive article')
@click.option('--browser', '-b', is_flag=True,
              default=False,
              help='Open in browser')
def random_article(browser, archive):
    articles = pocket_app.get_articles()
    article = random.choice(articles)

    print(format_article(article, header='Selected Article', line=True))

    if browser:
        webbrowser.open_new_tab(article['url'])

    if archive:
        pocket_app.archive_article(article['id'])


@click.command()
def fetch():
    try:
        pocket_app.fetch_articles(True)
    except AppNotConfigured:
        app_not_configured()
    except AppException as e:
        exception_occured(e)


@click.command(name='archive')
@click.argument('article_id')
def archive_article(article_id):
    try:
        pocket_app.archive_article(int(article_id))
    except AppNotConfigured:
        app_not_configured()
    except AppException as e:
        exception_occured(e)


def app_not_configured():
    print('App is not configured')
    print('Run `pocket-cli configure` to be able to use the app')


def exception_occured(exception):
    print('An error occured while '
          'trying to perform requested action: {}'.format(
              exception.message
          ))


main.add_command(configure)
main.add_command(add_article)
main.add_command(list_articles)
main.add_command(random_article)
main.add_command(fetch)
main.add_command(read)
main.add_command(archive_article)

if __name__ == '__main__':
    main()
