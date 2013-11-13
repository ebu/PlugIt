# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand


from django.conf import settings
import requests
from poplib import POP3
import email
import re
import base64
import hashlib
from plugIt.views import getPlugItObject
from plugIt.plugIt import PlugIt

class Command(BaseCommand):
    args = ''
    help = 'Check mails and forward them to PlugIt servers if needed'

    def handle(self, *args, **options):
        from Crypto.Cipher import AES

        
        pop_connection = POP3(settings.INCOMING_MAIL_HOST)
        pop_connection.user(settings.INCOMING_MAIL_USER)
        pop_connection.pass_(settings.INCOMING_MAIL_PASSWORD)
        
        numMessages = len(pop_connection.list()[1])
        for i in range(numMessages):
            data ='\n'.join(pop_connection.retr(i+1)[1])
            msg = email.message_from_string(data)

            ebuid = re.search(r'.\-{23}.\[([^ ]+)\]$', msg['Subject'])
            if ebuid:

                try:
                    base64encrypted_ebuid = ebuid.group(1)

                    encrypted_ebuid = base64.b64decode(base64encrypted_ebuid)

                    decrypter = AES.new(((settings.EBUIO_MAIL_SECRET_KEY) * 32)[:32], AES.MODE_CFB, '87447JEUPEBU4hR!')

                    decrypted_ebuid = decrypter.decrypt(encrypted_ebuid)
                except Exception as e:
                    print "Error with", msg['Subject'], e
                    continue

                (hash, data) = decrypted_ebuid.split(':', 1)

                expected_hash = hashlib.sha512(data + settings.EBUIO_MAIL_SECRET_HASH).hexdigest()[30:42]  # Substring to avoid long strings

                if expected_hash != hash:
                    print "Error with", msg['Subject'], "Unexpected hash !"
                    continue

                (projectid, data) = data.split(':', 1)

                if settings.PIAPI_STANDALONE:
                    plugIt = PlugIt(settings.PIAPI_STANDALONE_URI)
                else:
                    (plugIt, _, _) = getPlugItObject(projectid)

                payload = msg.get_payload()

                if isinstance(payload, list):  # If this is a multi-part mail, take the first part
                    payload = payload[0]

                if plugIt.newMail(data, payload):
                    print "Ok", msg['Subject']
                    pop_connection.dele(i+1)
        pop_connection.quit()
    