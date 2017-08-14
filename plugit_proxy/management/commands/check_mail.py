# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


from django.conf import settings
from poplib import POP3, POP3_SSL
import email
import re
import base64
import hashlib
from plugit_proxy.views import getPlugItObject
from plugit_proxy.plugIt import PlugIt


class Command(BaseCommand):
    args = ''
    help = 'Check mails and forward them to PlugIt servers if needed'

    def handle(self, *args, **options):
        from Crypto.Cipher import AES

        if int(getattr(settings, 'INCOMING_MAIL_PORT')) == 995:
            pop_connection = POP3_SSL(settings.INCOMING_MAIL_HOST, getattr(settings, 'INCOMING_MAIL_PORT'))
        else:
            pop_connection = POP3(settings.INCOMING_MAIL_HOST, getattr(settings, 'INCOMING_MAIL_PORT'))

        pop_connection.user(settings.INCOMING_MAIL_USER)
        pop_connection.pass_(settings.INCOMING_MAIL_PASSWORD)

        numMessages = len(pop_connection.list()[1])
        for i in range(numMessages):
            data = '\n'.join(pop_connection.retr(i + 1)[1])
            msg = email.message_from_string(data)

            # Extract part after the + in the email (notifications+<ID>@ebu.io)
            ebuid = re.search(r'^.*\+(.*)@.*$', msg['To'].replace('\r', '').replace('\n', ''))

            if ebuid:

                try:
                    base64encrypted_ebuid = ebuid.group(1)

                    encrypted_ebuid = base64.urlsafe_b64decode(base64encrypted_ebuid)

                    decrypter = AES.new(((settings.EBUIO_MAIL_SECRET_KEY) * 32)[:32], AES.MODE_CFB, '87447JEUPEBU4hR!')

                    decrypted_ebuid = decrypter.decrypt(encrypted_ebuid)
                except Exception as e:
                    print("Error with {} {}".format(msg['To'], e))
                    continue

                try:
                    (hash, data) = decrypted_ebuid.split(':', 1)
                except ValueError:
                    (hash, data) = (None, '')

                expected_hash = hashlib.sha512(data + settings.EBUIO_MAIL_SECRET_HASH).hexdigest()[30:42]  # Substring to avoid long strings

                if expected_hash != hash:
                    print("Error with {}, Unexpected hash !".format(msg['To']))
                    continue

                if 'x-auto-response-suppress' in msg \
                   or msg.get('Auto-Submitted', 'no') != 'no'  \
                   or 'Auto-Autorespond' in msg \
                   or 'auto-submitted' in msg \
                   or msg.get('precedence', None) in ['auto_reply', 'bluk', 'junk'] \
                   or msg.get('x-precedence', None) in ['auto_reply', 'bluk', 'junk']:
                        print("AutoResponse, dropped {}".format(msg['Subject']))
                        pop_connection.dele(i + 1)
                        continue

                (projectid, data) = data.split(':', 1)

                if settings.PIAPI_STANDALONE:
                    plugIt = PlugIt(settings.PIAPI_STANDALONE_URI)
                else:

                    if projectid == settings.DISCUSSION_ID:  # Special case for EBUIo/Discussions
                        from discuss.utils import mail_get_post
                        plugIt = mail_get_post(data)

                    else:
                        plugIt, _, _ = getPlugItObject(projectid)

                def get_first_text_part(msg):
                    maintype = msg.get_content_maintype()
                    if maintype == 'multipart':
                        for part in msg.get_payload():
                            if part.get_content_maintype() == 'text':
                                return part.get_payload(decode=True)
                    elif maintype == 'text':
                        return msg.get_payload(decode=True)

                payload = get_first_text_part(msg)

                if plugIt.newMail(data, payload):
                    print("Ok {}".format(msg['Subject']))
                    pop_connection.dele(i + 1)
        pop_connection.quit()
