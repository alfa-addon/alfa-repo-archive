# -*- coding: utf-8 -*-

import BaseHTTPServer
import traceback
from SocketServer import ThreadingMixIn
from threading import Thread


class Server(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    daemon_threads = True
    timeout = 1

    def __init__(self, address, handler, client):
        BaseHTTPServer.HTTPServer.__init__(self, address, handler)
        self._client = client
        self.file = None
        self.running = True
        self.request = None

    def stop(self):
        self.running = False

    def serve(self):
        while self.running:
            try:
                self.handle_request()
            except:
                print traceback.format_exc()

    def run(self):
        t = Thread(target=self.serve, name='HTTP Server')
        t.daemon = True
        t.start()

    def handle_error(self, request, client_address):
        if not "socket.py" in traceback.format_exc():
            print traceback.format_exc()
