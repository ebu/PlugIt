from test_proxyviews import TestProxyViews


from django.core import mail


import uuid
import json
import re
import base64
import hashlib
from Crypto.Cipher import AES


class TestProxyViewsViews(TestProxyViews):

    def set_check_false(self):
        self.views.check_api_key_bpk = self.views.check_api_key

        def no(self, *args, **kwargs):
            return False

        self.views.check_api_key = no

    def set_check_back(self):
        self.views.check_api_key = self.views.check_api_key_bpk

    def test_home_view(self):
        assert(self.views.api_home(self.build_request('/')).content.strip() == "API")

    def test_home_view_check(self):
        self.set_check_false()
        assert(self.views.api_home(self.build_request('/')).status_code == 403)
        self.set_check_back()

    def test_user_view(self):

        id = str(uuid.uuid4())

        response = self.views.api_user(self.build_request('/'), id)

        response_data = json.loads(response.content)

        assert(response_data['id'] == id)
        assert(response_data['pk'] == id)
        assert(not response_data['orgas'])

    def test_user_view_not_found(self):

        assert(self.views.api_user(self.build_request('/'), -100).status_code == 404)

    def test_user_view_fake_orgras(self):

        uid = str(uuid.uuid4())
        orga = str(uuid.uuid4())

        def generate_user(*args, **kwargs):

            class Orga():
                pk = orga[1:5]
                name = orga[6:10]
                ebu_codops = orga[11:15]

            class User():
                id = uid
                pk = uid

                def getOrgas(self, *args, **kwargs):
                    return [(Orga(), orga[0] in '13579')]

            return User()

        self.views.generate_user_bkp = self.views.generate_user
        self.views.generate_user = generate_user

        response = self.views.api_user(self.build_request('/'), id)

        response_data = json.loads(response.content)

        print(response_data)

        assert(response_data['orgas'])
        assert(response_data['orgas'][0]['is_admin'] == (orga[0] in '13579'))
        assert(response_data['orgas'][0]['id'] == orga[1:5])
        assert(response_data['orgas'][0]['name'] == orga[6:10])
        assert(response_data['orgas'][0]['codops'] == orga[11:15])

        self.views.generate_user = self.views.generate_user_bkp

    def test_user_view_check(self):
        self.set_check_false()
        assert(self.views.api_user(self.build_request('/'), 1).status_code == 403)
        self.set_check_back()

    def test_user_uuid_view_check(self):
        self.set_check_false()
        assert(self.views.api_user_uuid(self.build_request('/'), 1).status_code == 403)
        self.set_check_back()

    def test_subscriptions_view_check(self):
        self.set_check_false()
        assert(self.views.api_subscriptions(self.build_request('/'), 1).status_code == 403)
        self.set_check_back()

    def test_orga_view_ebu(self):

        response = json.loads(self.views.api_orga(self.build_request('/'), "-1").content)

        assert(response['pk'] == "-1")
        assert(response['name'] == 'EBU')
        assert(response['codops'] == 'zzebu')

    def test_orga_view_rts(self):

        response = json.loads(self.views.api_orga(self.build_request('/'), "-2").content)

        assert(response['pk'] == "-2")
        assert(response['name'] == 'RTS')
        assert(response['codops'] == 'chrts')

    def test_orga_view_bbc(self):

        response = json.loads(self.views.api_orga(self.build_request('/'), "-3").content)

        assert(response['pk'] == "-3")
        assert(response['name'] == 'BBC')
        assert(response['codops'] == 'gbbbc')

    def test_orga_view_cnn(self):

        response = json.loads(self.views.api_orga(self.build_request('/'), "-4").content)

        assert(response['pk'] == "-4")
        assert(response['name'] == 'CNN')
        assert(response['codops'] == 'uscnn')

    def test_orga_view_dummy(self):

        pk = str(uuid.uuid4())

        response = json.loads(self.views.api_orga(self.build_request('/'), pk).content)

        assert(response['pk'] == pk)
        assert('name' not in response)
        assert('codops'not in response)

    def test_orga_view_check(self):
        self.set_check_false()
        assert(self.views.api_orga(self.build_request('/'), 1).status_code == 403)
        self.set_check_back()

    def test_projects_members(self):

        response = json.loads(self.views.api_get_project_members(self.build_request('/')).content)

        assert(len(response['members']) == 3)
        assert(response['members'][0]['pk'] == -1)
        assert(response['members'][0]['id'] == "-1")
        assert(response['members'][1]['pk'] == -2)
        assert(response['members'][1]['id'] == "-2")
        assert(response['members'][2]['pk'] == -3)
        assert(response['members'][2]['id'] == "-3")

    def test_projects_members_check(self):
        self.set_check_false()
        assert(self.views.api_get_project_members(self.build_request('/')).status_code == 403)
        self.set_check_back()

    def test_generic_send_mail_no_config(self):

        mail.outbox = []

        self.views.settings.EBUIO_MAIL_SECRET_KEY = None
        self.views.settings.EBUIO_MAIL_SECRET_HASH = None

        sender = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        dest = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        subject = str(uuid.uuid4())
        message = str(uuid.uuid4())

        assert(not self.views.generic_send_mail(sender, [dest], subject, message, None))

        assert(not mail.outbox)

    def test_generic_send_mail_config(self):

        mail.outbox = []

        self.views.settings.EBUIO_MAIL_SECRET_KEY = str(uuid.uuid4())
        self.views.settings.EBUIO_MAIL_SECRET_HASH = str(uuid.uuid4())

        assert(not self.views.generic_send_mail(None, None, None, None, None))
        assert(not mail.outbox)

    def test_generic_send_mail(self):

        mail.outbox = []

        self.views.settings.EBUIO_MAIL_SECRET_KEY = str(uuid.uuid4())
        self.views.settings.EBUIO_MAIL_SECRET_HASH = str(uuid.uuid4())

        sender = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        dest = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        subject = str(uuid.uuid4())
        message = str(uuid.uuid4())

        assert(not self.views.generic_send_mail(sender, [dest], subject, message, None))
        assert(mail.outbox)

        assert(mail.outbox[0].subject == subject)
        assert(mail.outbox[0].from_email == sender)
        assert(mail.outbox[0].to[0] == dest)
        assert(mail.outbox[0].body == message)

    def test_generic_send_mail_html(self):

        mail.outbox = []

        self.views.settings.EBUIO_MAIL_SECRET_KEY = str(uuid.uuid4())
        self.views.settings.EBUIO_MAIL_SECRET_HASH = str(uuid.uuid4())

        sender = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        dest = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        subject = str(uuid.uuid4())
        message = str(uuid.uuid4())

        assert(not self.views.generic_send_mail(sender, [dest], subject, message, None, html_message=True))
        assert(mail.outbox)

        assert(mail.outbox[0].subject == subject)
        assert(mail.outbox[0].from_email == sender)
        assert(mail.outbox[0].to[0] == dest)
        assert(mail.outbox[0].body == message)
        assert(mail.outbox[0].content_subtype == 'html')

    def test_generic_send_mail_key(self):

        mail.outbox = []

        self.views.settings.EBUIO_MAIL_SECRET_KEY = str(uuid.uuid4())
        self.views.settings.EBUIO_MAIL_SECRET_HASH = str(uuid.uuid4())
        self.views.settings.MAIL_SENDER = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())

        sender = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        dest = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        subject = str(uuid.uuid4())
        message = str(uuid.uuid4())
        key = str(uuid.uuid4())

        assert(not self.views.generic_send_mail(sender, [dest], subject, message, key))
        assert(mail.outbox)

        assert(mail.outbox[0].subject == subject)
        assert(mail.outbox[0].from_email == sender)
        assert(mail.outbox[0].to[0] == dest)
        assert(mail.outbox[0].body == message)
        assert('Reply-To' in mail.outbox[0].extra_headers)

        rt = mail.outbox[0].extra_headers['Reply-To']

        assert(rt.startswith('{}+'.format(self.views.settings.MAIL_SENDER.split('@')[0])))
        assert(rt.endswith('@{}'.format(self.views.settings.MAIL_SENDER.split('@')[1])))

        ebuid = re.search(r'^.*\+(.*)@.*$', rt)

        assert(ebuid)

        base64encrypted_ebuid = ebuid.group(1)

        encrypted_ebuid = base64.urlsafe_b64decode(base64encrypted_ebuid)

        decrypter = AES.new(((self.views.settings.EBUIO_MAIL_SECRET_KEY) * 32)[:32], AES.MODE_CFB, '87447JEUPEBU4hR!')

        decrypted_ebuid = decrypter.decrypt(encrypted_ebuid)

        (hash, data) = decrypted_ebuid.split(':', 1)

        expected_hash = hashlib.sha512(data + self.views.settings.EBUIO_MAIL_SECRET_HASH).hexdigest()[30:42]

        assert(expected_hash == hash)
        assert(data == key)

    def test_send_mail(self):

        mail.outbox = []

        self.views.settings.EBUIO_MAIL_SECRET_KEY = str(uuid.uuid4())
        self.views.settings.EBUIO_MAIL_SECRET_HASH = str(uuid.uuid4())
        self.views.settings.MAIL_SENDER = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())

        sender = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        dest = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        subject = str(uuid.uuid4())
        message = str(uuid.uuid4())

        r = self.factory.post('/', {
            'sender': sender,
            'dests': [dest],
            'subject': subject,
            'message': message,
        })

        assert(self.views.api_send_mail(r))
        assert(mail.outbox)

        assert(mail.outbox[0].subject == subject)
        assert(mail.outbox[0].from_email == sender)
        assert(mail.outbox[0].to[0] == dest)
        assert(mail.outbox[0].body == message)

    def test_send_mail_html(self):

        mail.outbox = []

        self.views.settings.EBUIO_MAIL_SECRET_KEY = str(uuid.uuid4())
        self.views.settings.EBUIO_MAIL_SECRET_HASH = str(uuid.uuid4())
        self.views.settings.MAIL_SENDER = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())

        sender = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        dest = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        subject = str(uuid.uuid4())
        message = str(uuid.uuid4())

        r = self.factory.post('/', {
            'sender': sender,
            'dests': [dest],
            'subject': subject,
            'message': message,
            'html_message': True,
        })

        assert(self.views.api_send_mail(r))
        assert(mail.outbox)

        assert(mail.outbox[0].subject == subject)
        assert(mail.outbox[0].from_email == sender)
        assert(mail.outbox[0].to[0] == dest)
        assert(mail.outbox[0].body == message)
        assert(mail.outbox[0].content_subtype == 'html')

    def test_send_mail_no_sender(self):

        mail.outbox = []

        self.views.settings.EBUIO_MAIL_SECRET_KEY = str(uuid.uuid4())
        self.views.settings.EBUIO_MAIL_SECRET_HASH = str(uuid.uuid4())
        self.views.settings.MAIL_SENDER = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())

        dest = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        subject = str(uuid.uuid4())
        message = str(uuid.uuid4())

        r = self.factory.post('/', {
            'dests': [dest],
            'subject': subject,
            'message': message,
            'html_message': True,
        })

        assert(self.views.api_send_mail(r))
        assert(mail.outbox)

        assert(mail.outbox[0].subject == subject)
        assert(mail.outbox[0].from_email == self.views.settings.MAIL_SENDER)
        assert(mail.outbox[0].to[0] == dest)
        assert(mail.outbox[0].body == message)
        assert(mail.outbox[0].content_subtype == 'html')

    def test_send_mail_key(self):

        mail.outbox = []

        self.views.settings.EBUIO_MAIL_SECRET_KEY = str(uuid.uuid4())
        self.views.settings.EBUIO_MAIL_SECRET_HASH = str(uuid.uuid4())
        self.views.settings.MAIL_SENDER = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())

        sender = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        dest = '{}@{}.com'.format(uuid.uuid4(), uuid.uuid4())
        subject = str(uuid.uuid4())
        message = str(uuid.uuid4())
        key = str(uuid.uuid4())

        r = self.factory.post('/', {
            'sender': sender,
            'dests': [dest],
            'subject': subject,
            'message': message,
            'response_id': key,
        })

        assert(self.views.api_send_mail(r, None, ''))
        assert(mail.outbox)

        assert(mail.outbox[0].subject == subject)
        assert(mail.outbox[0].from_email == sender)
        assert(mail.outbox[0].to[0] == dest)
        assert(mail.outbox[0].body == message)

        assert('Reply-To' in mail.outbox[0].extra_headers)

        rt = mail.outbox[0].extra_headers['Reply-To']

        assert(rt.startswith('{}+'.format(self.views.settings.MAIL_SENDER.split('@')[0])))
        assert(rt.endswith('@{}'.format(self.views.settings.MAIL_SENDER.split('@')[1])))

        ebuid = re.search(r'^.*\+(.*)@.*$', rt)

        assert(ebuid)

        base64encrypted_ebuid = ebuid.group(1)

        encrypted_ebuid = base64.urlsafe_b64decode(base64encrypted_ebuid)

        decrypter = AES.new(((self.views.settings.EBUIO_MAIL_SECRET_KEY) * 32)[:32], AES.MODE_CFB, '87447JEUPEBU4hR!')

        decrypted_ebuid = decrypter.decrypt(encrypted_ebuid)

        (hash, data) = decrypted_ebuid.split(':', 1)

        expected_hash = hashlib.sha512(data + self.views.settings.EBUIO_MAIL_SECRET_HASH).hexdigest()[30:42]

        assert(expected_hash == hash)
        assert(data == ':{}'.format(key))

    def test_send_mail_check(self):
        self.set_check_false()
        assert(self.views.api_send_mail(self.build_request('/')).status_code == 403)
        self.set_check_back()

    def test_orgas(self):

        response = json.loads(self.views.api_orgas(self.build_request('/')).content)

        assert('data' in response)
        assert(len(response['data']) == 4)
        assert(response['data'][0]['id'] == -1)
        assert(response['data'][0]['name'] == 'EBU')
        assert(response['data'][0]['codops'] == 'ZZEBU')
        assert(response['data'][1]['id'] == -2)
        assert(response['data'][1]['name'] == 'RTS')
        assert(response['data'][1]['codops'] == 'CHRTS')
        assert(response['data'][2]['id'] == -3)
        assert(response['data'][2]['name'] == 'BBC')
        assert(response['data'][2]['codops'] == 'GBEBU')
        assert(response['data'][3]['id'] == -4)
        assert(response['data'][3]['name'] == 'CNN')
        assert(response['data'][3]['codops'] == 'USCNN')

    def test_orgas_check(self):
        self.set_check_false()
        assert(self.views.api_orgas(self.build_request('/')).status_code == 403)
        self.set_check_back()

    def test_ebuio_forum(self):
        response = json.loads(self.views.api_ebuio_forum(self.build_request('/')).content)
        assert('error' in response)

    def test_ebuio_forum_check(self):
        self.set_check_false()
        assert(self.views.api_ebuio_forum(self.build_request('/')).status_code == 403)
        self.set_check_back()

    def test_ebuio_forum_get_topics_by_tag_for_user(self):
        response = json.loads(self.views.api_ebuio_forum_get_topics_by_tag_for_user(self.build_request('/')).content)
        assert('error' in response)

    def test_ebuio_forum_get_topics_by_tag_for_user_check(self):
        self.set_check_false()
        assert(self.views.api_ebuio_forum_get_topics_by_tag_for_user(self.build_request('/')).status_code == 403)
        self.set_check_back()
