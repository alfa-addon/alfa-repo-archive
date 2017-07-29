# -*- coding: utf-8 -*-

from threading import Thread, Lock, Event


class Monitor(Thread):
    def __init__(self, client):
        Thread.__init__(self)
        self.daemon = True
        self.listeners = []
        self.lock = Lock()
        self.wait_event = Event()
        self.running = True
        self.client = client
        self.ses = None
        self.client = client

    def stop(self):
        self.running = False
        self.wait_event.set()

    def add_listener(self, cb):
        with self.lock:
            if not cb in self.listeners:
                self.listeners.append(cb)

    def remove_listener(self, cb):
        with self.lock:
            try:
                self.listeners.remove(cb)
            except ValueError:
                pass

    def remove_all_listeners(self):
        with self.lock:
            self.listeners = []

    def run(self):
        while (self.running):
            with self.lock:
                for cb in self.listeners:
                    cb()

            self.wait_event.wait(1.0)
