# -*- coding: utf-8 -*-

class ResumeData(object):
    def __init__(self, client):
        self.data = None
        self.failed = False
        client._dispatcher.add_listener(self._process_alert)
        client._th.save_resume_data()

    def _process_alert(self, t, alert):
        if t == 'save_resume_data_failed_alert':
            self.failed = True

        elif t == 'save_resume_data_alert':
            self.data = alert.resume_data
