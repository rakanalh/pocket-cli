import random
import subprocess
import sys
import webbrowser

import click

from .app import PocketApp
from .utils import format_article


pocket_app = PocketApp()

WORDS_PER_MINUTE = 180


@click.group()
def main():
    pass


@click.command()
@click.option('--consumer-key', '-k',
              prompt='Please provide your consumer key')
@click.option('--access-token', '-t',
              prompt='Please provide your access token')
@click.option('--words-per-minute', '-wpm',
              type=click.INT,
              prompt='Please prefer your reading speed in words per minute',
              help='Used in calculating reading time for each article')
def configure():
    pass


@click.command(name='list')
@click.option('--limit', '-l', default=10,
              help='Number of items to list')
@click.option('--order', '-o', default='asc',
              type=click.Choice(['asc', 'desc']),
              help='Order of items to return')
def list_articles(limit, order):
    articles = pocket_app.get_articles(limit, order)

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
    pocket_app.fetch_articles(True)


main.add_command(configure)
main.add_command(list_articles)
main.add_command(random_article)
main.add_command(fetch)
main.add_command(read)

if __name__ == '__main__':
    main()
