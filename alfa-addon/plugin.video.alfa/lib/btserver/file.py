# -*- coding: utf-8 -*-

import os

from cursor import Cursor


class File(object):
    def __init__(self, path, base, index, size, fmap, piece_size, client):
        self._client = client
        self.path = path
        self.base = base
        self.index = index
        self.size = size

        self.piece_size = piece_size

        self.full_path = os.path.join(base, path)
        self.first_piece = fmap.piece
        self.offset = fmap.start
        self.last_piece = self.first_piece + max((size - 1 + fmap.start), 0) // piece_size

        self.cursor = None

    def create_cursor(self, offset=None):
        self.cursor = Cursor(self)
        if offset:
            self.cursor.seek(offset)
        return self.cursor

    def map_piece(self, ofs):
        return self.first_piece + (ofs + self.offset) // self.piece_size, (ofs + self.offset) % self.piece_size

    def update_piece(self, n, data):
        if self.cursor:
            self.cursor.update_piece(n, data)

    def __str__(self):
        return self.path
