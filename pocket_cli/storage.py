import csv
import os


class Storage:
    def __init__(self):
        self._filename = '{}/.pocket-time-index'.format(
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

        with open(self._filename, 'a+') as csv_file:
            dict_writer = csv.DictWriter(csv_file, data[0].keys())
            if write_header:
                dict_writer.writeheader()

            dict_writer.writerows(data)

    def read(self, limit=10, order='asc'):
        index = []

        if not os.path.exists(self._filename):
            return index

        row_counter = 0
        with open(self._filename, 'r') as csv_file:
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
