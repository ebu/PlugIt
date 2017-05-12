import unittest


import sys
import os


class _CallBack():
    def __init__(self, prop_to_set):
        for (key, value) in prop_to_set.items():
            setattr(self, key, value)


class TestBase(unittest.TestCase):
    """Common class for tests"""

    DUMMY_CONFIG_PATH = os.path.join('tests', 'dummy_config')

    @classmethod
    def setup_class(cls):
        """Setup path"""
        sys.path.append(cls.DUMMY_CONFIG_PATH)

    @classmethod
    def teardown_class(cls):
        """Remove added value from path"""
        sys.path.remove(cls.DUMMY_CONFIG_PATH)
