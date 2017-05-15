from _utils import TestBase


from django.conf import settings


import sys
import uuid
import subprocess
import time


class TestCheckMail(TestBase):

    @classmethod
    def setup_class(cls):
        super(TestCheckMail, cls).setup_class()
        cls.start_popserver()
        time.sleep(1)
        cls.run_checkmail()
        cls.stop_popserver()

    @classmethod
    def start_popserver(cls):
        cls.p = subprocess.Popen([sys.executable, 'server.py'], cwd='tests/helpers/pop_server', stderr=subprocess.PIPE)

    @classmethod
    def stop_popserver(cls):
        (out, err) = cls.p.communicate()
        cls.output = err

    @classmethod
    def run_checkmail(cls):
        cls.pop_user = str(uuid.uuid4())
        cls.pop_password = str(uuid.uuid4())

        settings.INCOMING_MAIL_HOST = "127.0.0.1"
        settings.INCOMING_MAIL_PORT = 22110
        settings.INCOMING_MAIL_USER = cls.pop_user
        settings.INCOMING_MAIL_PASSWORD = cls.pop_password
        settings.EBUIO_MAIL_SECRET_HASH = 'secret-for-tests'
        settings.EBUIO_MAIL_SECRET_KEY = 'secret2-for-tests'

        from plugit_proxy.management.commands import check_mail

        mail_handeled = []

        # False plugit object to capture mail sends
        class DummyPlugIt:
            def __init__(self, *args, **kwargs):
                pass

            def newMail(self, data, payload):
                mail_handeled.append((data, payload))
                return True

        check_mail.PlugIt = DummyPlugIt

        check_mail.Command().handle()

        cls.mail_handeled = mail_handeled

    def test_output(self):
        assert(self.output)

    def test_user(self):
        """Test that the command logged in"""

        assert("USER:%s\n" % (self.pop_user,) in self.output)

    def test_password(self):
        """Test that the command sent the correct password"""

        assert("PASS:%s\n" % (self.pop_password,) in self.output)

    def test_mail1_retrived(self):
        """Mail1 should have been retrivied"""
        assert("RETRIVE:1\n" in self.output)

    def test_mail1_not_deleted(self):
        """Mail1 should not have been deleted"""
        assert("DELETE:1\n" not in self.output)

    def test_mail2_retrived(self):
        """Mail2 should have been retrivied"""
        assert("RETRIVE:2\n" in self.output)

    def test_mail2_not_deleted(self):
        """Mail2 should not have been deleted"""
        assert("DELETE:2\n" not in self.output)

    def test_mail3_retrived(self):
        """Mail3 should have been retrivied"""
        assert("RETRIVE:3\n" in self.output)

    def test_mail3_not_deleted(self):
        """Mail3 should not have been deleted"""
        assert("DELETE:3\n" not in self.output)

    def test_mail4_retrived(self):
        """Mail4 should have been retrivied"""
        assert("RETRIVE:4\n" in self.output)

    def test_mail4_not_deleted(self):
        """Mail4 should not have been deleted"""
        assert("DELETE:4\n" not in self.output)

    def test_mail5_retrived(self):
        """Mail5 should have been retrivied"""
        assert("RETRIVE:5\n" in self.output)

    def test_mail5_not_deleted(self):
        """Mail5 should not have been deleted"""
        assert("DELETE:5\n" not in self.output)

    def test_mail6_retrived(self):
        """Mail6 should have been retrivied"""
        assert("RETRIVE:6\n" in self.output)

    def test_mail6_not_deleted(self):
        """Mail6 should have been deleted"""
        assert("DELETE:6\n" in self.output)

    def test_mail6_handeled(self):
        """Mail6 should has been handeled"""
        assert(('test', 'ThisIsMail6\n\n') in self.mail_handeled)

    def test_mail7_retrived(self):
        """Mail7 should have been retrivied"""
        assert("RETRIVE:7\n" in self.output)

    def test_mail7_not_deleted(self):
        """Mail7 should have been deleted"""
        assert("DELETE:7\n" in self.output)

    def test_mail7_handeled(self):
        """Mail7 should has been handeled"""
        assert(('test', 'ThisIsMail7\n\n') in self.mail_handeled)

    def test_mail891011121314151617_retrived(self):
        """Mail with auto response should have been retrivied"""
        for i in range(8, 18):
            print("Testing", i,)
            assert("RETRIVE:" + str(i) + "\n" in self.output)
            print("OK")

    def test_mail891011121314151617_not_deleted(self):
        """Mail with auto response should have been deleted"""
        for i in range(8, 18):
            print("Testing", i,)
            assert("DELETE:" + str(i) + "\n" in self.output)
            print("OK")

    def test_mail891011121314151617_handeled(self):
        """Mail with auto response should NOT has been handeled"""
        for i in range(8, 18):
            print("Testing", i,)
            assert(('test', 'ThisIsMail%s\n\n' % (str(i),)) not in self.mail_handeled)
            print("OK")
