import unittest


from django.conf import settings
import os
import sys


settings.configure(LOGGING_CONFIG=None, PIAPI_STANDALONE=True, PIAPI_BASEURI="/plugIt/", PIAPI_ORGAMODE=True, PIAPI_REALUSERS=False, PIAPI_PROXYMODE=False, PIAPI_PLUGITMENUACTION='menubar', PIAPI_STANDALONE_URI='http://127.0.0.1:63441', TEMPLATE_DIRS=('tests/templates',), PIAPI_USERDATA=['k', 'pk'], PIAPI_PLUGITTEMPLATE=None)


class TestBase(unittest.TestCase):
    """Common class for tests"""

    STANDALONE_PROXY = os.path.join('examples', 'standalone_proxy')

    @classmethod
    def setup_class(self):
        """Setup path"""
        sys.path.append(self.STANDALONE_PROXY)

    @classmethod
    def teardown_class(self):
        """Remove added value from path"""
        sys.path.remove(self.STANDALONE_PROXY)
