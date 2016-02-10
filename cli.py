import configparser
import csv
import math
import os
import random
import shutil
import subprocess
import sys
import webbrowser
from operator import itemgetter

import click
import pocket
from progress.spinner import Spinner

WORDS_PER_MINUTE = 180


@click.group()
def main():
    pass


@click.command(name='list')
@click.option('--limit', '-l', default=10,
              help='Number of items to list')
@click.option('--order', '-o', default='asc',
              type=click.Choice(['asc', 'desc']),
              help='Order of items to return')
def list_articles(limit, order):
    articles = get_index(limit, order)

    try:
        pager = subprocess.Popen(['less'],
                                 stdin=subprocess.PIPE,
                                 stdout=sys.stdout)
        for article in articles:
            if int(article['reading_time']) <= 0:
                article['reading_time'] = 'Unknown'

            pager.stdin.write(b'=' * shutil.get_terminal_size()[0])
            pager.stdin.write(
                '{} - {}\nReading Time: {} Mins\nURL: {}\n'.format(
                    article['id'],
                    article['title'] if article['title'] else '(No Title)',
                    article['reading_time'],
                    article['url']
                ).encode('utf-8')
            )
        pager.stdin.close()
        pager.wait()
    except (KeyboardInterrupt, ValueError):
        # let less handle this, -K will exit cleanly
        pass


@click.command(name='random')
@click.option('--archive/--no-archive', '-a/-na',
              default=False,
              help='Archive article')
@click.option('--browser/--no-browser', '-b/-nb',
              default=False,
              help='Open in browser')
def random_article(browser, archive):
    articles = get_index()
    article = random.choice(articles)

    print('=' * shutil.get_terminal_size()[0])
    print('Selected Article:\n{} - {}\nReading Time: {} Mins\nURL: {}'.format(
        article['id'],
        article['title'],
        article['reading_time'],
        article['url']
    ))
    print('=' * shutil.get_terminal_size()[0])

    if browser:
        webbrowser.open_new_tab(article['url'])

    if archive:
        archive_article(article['id'])


@click.command()
def fetch():
    configs = get_configs(None)

    try:
        wpm = configs.get('reading', 'words_per_minute')
    except (configparser.NoSectionError, configparser.NoOptionError):
        wpm = None

    if not wpm:
        wpm = WORDS_PER_MINUTE

    pocket_instance = pocket.Pocket(
        configs.get('auth', 'consumer_key'),
        configs.get('auth', 'access_token')
    )

    articles_index = []

    spinner = Spinner('Loading articles ')

    offset = 0
    count = 20
    while(True):
        articles = pocket_instance.retrieve(
            state='unread',
            count=count,
            offset=offset
        )

        print(articles)

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
        spinner.next()

    articles_index = sorted(articles_index,
                            key=itemgetter('reading_time'))
    store_index(articles_index)


def archive_article(item_id):
    configs = get_configs(None)

    pocket_instance = pocket.Pocket(
        configs.get('auth', 'consumer_key'),
        configs.get('auth', 'access_token')
    )

    pocket_instance.archive(int(item_id)).commit()


def get_index(limit=10, order='asc'):
    index = []
    filename = '{}/.pocket-time-index'.format(os.path.expanduser('~'))

    row_counter = 0
    with open(filename, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            index.append(row)

            if order == 'asc':
                row_counter += 1
            if row_counter == limit:
                break

    if order == 'desc':
        index = index[::-1]

    return index[0:limit]


def store_index(index_data):
    filename = '{}/.pocket-time-index'.format(os.path.expanduser('~'))
    with open(filename, 'w') as csv_file:
        dict_writer = csv.DictWriter(csv_file, index_data[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(index_data)


def get_configs(path):
    if path is not None and not os.path.exists(path):
        raise ValueError('Path {} does not exist'.format(path))

    if path is None:
        path = '{}/.pocket-time'.format(os.path.expanduser('~'))

    config_parser = configparser.ConfigParser()
    config_parser.readfp(open(path))

    return config_parser

main.add_command(list_articles)
main.add_command(random_article)
main.add_command(fetch)

if __name__ == '__main__':
    main()
