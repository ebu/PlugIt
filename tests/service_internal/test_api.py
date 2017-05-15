from _utils import TestBase


from nose.tools import *


import os
import uuid
import requests


class TestApi(TestBase):
    """Test the api.py file"""

    @classmethod
    def setup_class(cls):
        super(TestApi, cls).setup_class()

        cls.user_key = str(uuid.uuid4())
        cls.orgas_key = str(uuid.uuid4())
        cls.orga_key = str(uuid.uuid4())
        cls.project_members_key = str(uuid.uuid4())
        cls.send_mail_key = str(uuid.uuid4())
        cls.forum_key = str(uuid.uuid4())

        from plugit.api import PlugItAPI
        cls.api = PlugItAPI('http://127.0.0.1:62312/')

        import subprocess
        import sys
        import time

        FNULL = open(os.devnull, 'w')
        cls.p = subprocess.Popen([sys.executable, 'tests/helpers/api_server.py', cls.user_key, cls.orgas_key, cls.orga_key, cls.project_members_key, cls.send_mail_key, cls.forum_key], stdout=FNULL, stderr=FNULL)

        for x in range(50):
            try:
                requests.get('http://127.0.0.1:62312')
                return
            except:
                time.sleep(0.1)

    @classmethod
    def teardown_class(cls):
        super(TestApi, cls).teardown_class()

        cls.p.kill()

    def test_get_user(self):
        """Test the get_user call"""

        retour = self.api.get_user(self.user_key[3])

        assert(retour)
        assert(retour.pk == self.user_key[3])
        assert(retour.id == self.user_key[3])
        assert(getattr(retour, self.user_key[::-1]) == self.user_key)

    def test_get_user_unknown(self):
        """Test the get_user call"""

        retour = self.api.get_user('not-a-user')

        assert(not retour)

    def test_subscriptions(self):
        """Test the get_subscription_labels call"""

        retour = self.api.get_subscription_labels(self.user_key[3])
        assert(retour)
        assert('test_subscription' in retour)

    def test_subscriptions_unknown(self):
        """Test the get_subscription_labels call"""
        assert(not self.api.get_subscription_labels('not-a-user'))

    def test_get_orgas(self):
        """Test the get_orgas call"""

        retour = self.api.get_orgas()

        assert(retour)
        assert(len(retour) == len(self.orgas_key))
        for x in self.orgas_key:
            o = retour.pop(0)
            assert(o.id == x)
            assert(o.pk == x)
            assert(getattr(o, self.orgas_key.replace(x, '')[::-1]) == self.orgas_key.replace(x, ''))

    def test_get_orga(self):
        """Test the get_orga call"""

        retour = self.api.get_orga(self.orga_key[3])

        assert(retour)
        assert(retour.pk == self.orga_key[3])
        assert(retour.id == self.orga_key[3])
        assert(getattr(retour, self.orga_key[::-1]) == self.orga_key)

    def test_get_orga_unknown(self):
        """Test the get_orga call"""

        retour = self.api.get_orga('not-an-orga')

        assert(not retour)

    def test_get_project_members(self):
        """Test the get_project_members call"""

        retour = self.api.get_project_members()

        assert(retour)
        assert(len(retour) == len(self.project_members_key))

        for x in self.project_members_key:
            o = retour.pop(0)
            assert(o.id == x)
            assert(getattr(o, self.project_members_key.replace(x, '')[::-1]) == self.project_members_key.replace(x, ''))

    def test_send_mail(self):
        """Test the send mail call"""

        retour = self.api.send_mail(self.send_mail_key[1], self.send_mail_key[5], [self.send_mail_key[0], self.send_mail_key[4]], self.send_mail_key[9])

        assert(retour)
        assert(retour.text == self.send_mail_key)

    def test_send_mail_2(self):
        """Test the send mail call, with a response_id"""

        retour = self.api.send_mail(self.send_mail_key[1], self.send_mail_key[5], [self.send_mail_key[0], self.send_mail_key[4]], self.send_mail_key[9], self.send_mail_key[7])

        assert(retour)
        assert(retour.text == self.send_mail_key[::-1])

    def test_ebuio_forum(self):
        """Test the ebuio_forum call"""
        retour = self.api.ebuio_forum(self.forum_key[2], self.forum_key[6], self.forum_key[10])

        assert(retour)
        assert(retour['key'] == self.forum_key)

    def test_ebuio_forum_tags_no_tag(self):
        """Test the ebuio_forum_tags call"""
        retour = self.api.forum_topic_get_by_tag_for_user()
        assert(not retour)

    def test_ebuio_forum_tags_no_author_empty(self):
        """Test the ebuio_forum_tags call"""
        retour = self.api.forum_topic_get_by_tag_for_user(self.forum_key[2])
        assert(not retour)

    def test_ebuio_forum_tags_no_author(self):
        """Test the ebuio_forum_tags call"""
        retour = self.api.forum_topic_get_by_tag_for_user(self.forum_key[3])
        assert(retour)
        assert(self.forum_key[3] in retour)

    def test_ebuio_forum_tags_author(self):
        """Test the ebuio_forum_tags call"""
        retour = self.api.forum_topic_get_by_tag_for_user(self.forum_key[3], self.forum_key[6])
        assert(retour)
        assert(self.forum_key[6] in retour)
