# -*- coding: utf-8 -*-

from monitor import Monitor

try:
    from python_libtorrent import get_libtorrent

    lt = get_libtorrent()
except Exception, e:
    import libtorrent as lt


class Dispatcher(Monitor):
    def __init__(self, client):
        super(Dispatcher, self).__init__(client)

    def do_start(self, th, ses):
        self._th = th
        self._ses = ses
        self.start()

    def run(self):
        if not self._ses:
            raise Exception('Invalid state, session is not initialized')

        while self.running:
            a = self._ses.wait_for_alert(1000)
            if a:
                alerts = self._ses.pop_alerts()
                for alert in alerts:
                    with self.lock:
                        for cb in self.listeners:
                            cb(lt.alert.what(alert), alert)
