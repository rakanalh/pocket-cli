import os

try:
    from shutil import get_terminal_size
except ImportError:
    def get_terminal_size():
        def ioctl_GWINSZ(fd):
            try:
                import fcntl
                import termios
                import struct
                cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
                                                     '1234'))
            except:
                return None
            return cr
        cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
        if not cr:
            try:
                fd = os.open(os.ctermid(), os.O_RDONLY)
                cr = ioctl_GWINSZ(fd)
                os.close(fd)
            except:
                pass
        if not cr:
            try:
                cr = (os.env['LINES'], os.env['COLUMNS'])
            except:
                cr = (25, 80)
        return int(cr[1]), int(cr[0])


def format_article(article, header=None, footer=None, line=False):
    content = ''
    if header:
        content = '{}\n'.format(header)
    if line:
        content += '{}\n'.format('=' * (get_terminal_size()[0]-1))

    content += '{} - {}\nReading Time: {} Mins\nURL: {}\n'.format(
        article['id'],
        article['title'] if article['title'] else '(No Title)',
        article['reading_time'],
        article['url']
    )

    if footer:
        content += footer

    return content
