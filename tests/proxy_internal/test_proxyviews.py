from _utils import TestBase


import django
from django.test.utils import setup_test_environment, teardown_test_environment
from django.test import RequestFactory
import os
import sys
import uuid
import subprocess
import time
import requests


class TestProxyViews(TestBase):

    process_service = None

    @classmethod
    def setup_class(cls):
        super(TestProxyViews, cls).setup_class()

        django.setup()
        setup_test_environment()

        from plugit_proxy import views
        from plugit_proxy.plugIt import PlugIt

        cls.views = views
        cls.PlugIt = PlugIt

        cls.factory = RequestFactory()

        cls.start_process_service()

    @classmethod
    def teardown_class(cls):
        super(TestProxyViews, cls).teardown_class()
        teardown_test_environment()

        cls.process_service.kill()
        cls.process_service = None

    @classmethod
    def start_process_service(cls, args=[]):

        if cls.process_service:
            cls.process_service.kill()

        FNULL = open(os.devnull, 'w')
        cls.process_service = subprocess.Popen([sys.executable, 'server.py', '63441'] + args, cwd='tests/helpers/flask_server', stdout=FNULL, stderr=FNULL)

        for x in range(50):
            try:
                requests.get('http://127.0.0.1:63441')
                return
            except:
                time.sleep(0.1)

    def random_base_url(self):

        new_base_url = str(uuid.uuid4())

        self.views.baseURI_bkp = self.views.baseURI
        self.views.baseURI = new_base_url

        return new_base_url

    def restore_base_url(self):
        self.views.baseURI = self.views.baseURI_bkp

    def build_request(self, path, method='GET'):
        r = self.factory.get(path)
        r.session = {}
        r.method = method

        return r
