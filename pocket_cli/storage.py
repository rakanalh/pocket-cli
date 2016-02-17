from __future__ import unicode_literals

import csv
import os
import six


class Storage:
    def __init__(self):
        self._filename = '{}/.pocket-index'.format(
            os.path.expanduser('~'))

    def is_empty(self):
        if not os.path.exists(self._filename):
            return True

        if os.stat(self._filename).st_size == 0:
            return True

        return False

    def write(self, data):
        if not data:
            return

        write_header = False
        if self.is_empty():
            write_header = True

        with open(self._filename, 'a+b') as csv_file:
            dict_writer = csv.DictWriter(csv_file, data[0].keys())
            if write_header:
                dict_writer.writeheader()

            dict_writer.writerows(self._encode_data(data))

    def read(self, limit=10, order='asc'):
        index = []

        if not os.path.exists(self._filename):
            return index

        row_counter = 0
        with open(self._filename, 'rb') as csv_file:
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

    def clear(self):
        if os.path.exists(self._filename):
            os.remove(self._filename)

    def _encode_data(self, data):
        for index, item in enumerate(data):
            for key, value in item.items():
                if isinstance(value, six.string_types):
                    data[index][key] = value.encode('utf-8')
        return data
