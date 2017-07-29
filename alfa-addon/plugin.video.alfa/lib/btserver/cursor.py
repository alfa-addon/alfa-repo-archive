# -*- coding: utf-8 -*-

from threading import Lock, Event


class Cursor(object):
    def __init__(self, file):
        self._file = file
        self.pos = 0
        self.timeout = 30
        self.cache_size = self._file._client.buffer_size
        self.cache = {}
        self.lock = Lock()
        self.event = Event()
        self.cache_first = 0

    def fill_cache(self, first):
        self.cache_first = first

        with self.lock:
            for p in sorted(self.cache):
                if p < first: del self.cache[p]

        self.event.clear()
        for i in xrange(first, first + self.cache_size):
            if i <= self._file.last_piece:
                self._file._client.prioritize_piece(i, i - first)

    def has_piece(self, n):
        with self.lock:
            return n in self.cache

    def _wait_piece(self, pc_no):
        while not self.has_piece(pc_no):
            self.fill_cache(pc_no)
            self.event.wait(self.timeout)

    def _get_piece(self, n):
        with self.lock:
            if not n in self.cache:
                raise ValueError('index of of scope of current cache')
            return self.cache[n]

    def get_piece(self, n):
        self._wait_piece(n)
        return self._get_piece(n)

    def close(self):
        self._file.cursor = None

    def read(self, size=None):
        data = ""
        max_size = self._file.size - self.pos
        if not size:
            size = max_size
        else:
            size = min(size, max_size)

        if size:
            pc_no, ofs = self._file.map_piece(self.pos)
            data = self.get_piece(pc_no)[ofs: ofs + size]

            if len(data) < size:
                remains = size - len(data)
                pc_no += 1
                self.fill_cache(pc_no)
                while remains and self.has_piece(pc_no):
                    sz = min(remains, self._file.piece_size)
                    data += self.get_piece(pc_no)[:sz]
                    remains -= sz
                    if remains:
                        pc_no += 1
                    self.fill_cache(pc_no)

        self.pos += len(data)

        return data

    def seek(self, n):
        if n > self._file.size:
            n = self._file.size
        elif n < 0:
            raise ValueError('Seeking negative')
        self.pos = n

    def tell(self):
        return self.pos

    def update_piece(self, n, data):
        with self.lock:
            pcs = sorted(self.cache)
            if len(pcs) < self.cache_size:
                if len(pcs):
                    new = max(pcs) + 1
                else:
                    new = self.cache_first
                if n == new:
                    self.cache[n] = data
                    if n == self.cache_first:
                        self.event.set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
