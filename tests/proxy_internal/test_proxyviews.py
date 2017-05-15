from _utils import TestBase


import django
from django.test.utils import setup_test_environment, teardown_test_environment
from django.test import RequestFactory
import os
import sys
import uuid
import subprocess
import time


class TestProxyViews(TestBase):

    process_service = None

    @classmethod
    def setup_class(self):
        super(TestProxyViews, self).setup_class()

        django.setup()
        setup_test_environment()

        from plugit_proxy import views
        from plugit_proxy.plugIt import PlugIt

        self.views = views
        self.PlugIt = PlugIt

        self.factory = RequestFactory()

        self.start_process_service()

    @classmethod
    def teardown_class(self):
        super(TestProxyViews, self).teardown_class()
        teardown_test_environment()

        self.process_service.kill()
        self.process_service = None

    @classmethod
    def start_process_service(self, args=[]):

        if self.process_service:
            self.process_service.kill()

        FNULL = open(os.devnull, 'w')
        self.process_service = subprocess.Popen([sys.executable, 'server.py', '63441'] + args, cwd='tests/helpers/flask_server', stdout=FNULL, stderr=FNULL)
        time.sleep(0.5)

    def random_base_url(self):

        new_base_url = str(uuid.uuid4())

        self.views.baseURI_bkp = self.views.baseURI
        self.views.baseURI = new_base_url

        return new_base_url

    def restore_base_url(self):
        self.views.baseURI = self.views.baseURI_bkp

    def build_request(self, path):
        r = self.factory.get(path)
        r.session = {}

        return r
