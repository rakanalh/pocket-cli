import shutil


def format_article(article, header=None, footer=None, line=False):
    content = ''
    if header:
        content = header
    if line:
        content += '{}\n'.format('=' * (shutil.get_terminal_size()[0]-1))

    content += '{} - {}\nReading Time: {} Mins\nURL: {}\n'.format(
        article['id'],
        article['title'] if article['title'] else '(No Title)',
        article['reading_time'],
        article['url']
    )

    if footer:
        content += footer

    return content
