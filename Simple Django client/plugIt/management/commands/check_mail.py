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

        
        cox = POP3(settings.INCOMING_MAIL_HOST)
        cox.user(settings.INCOMING_MAIL_USER)
        cox.pass_(settings.INCOMING_MAIL_PASSWORD)
        
        numMessages = len(cox.list()[1])
        for i in range(numMessages):
            data ='\n'.join(cox.retr(i+1)[1])
            msg = email.message_from_string(data)

            ebuid = re.search(r'\-.IOId:([^ ]+)$', msg['Subject'])
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

                excepted_hash = hashlib.sha512(data + settings.EBUIO_MAIL_SECRET_HASH).hexdigest()[30:42]

                if excepted_hash != hash:
                    print "Error with", msg['Subject'], "Unexecpted hash !"
                    continue

                (projectid, data) = data.split(':', 1)

                if settings.PIAPI_STANDALONE:
                    plugIt = PlugIt(settings.PIAPI_STANDALONE_URI)
                else:
                    (plugIt, _, _) = getPlugItObject(projectid)

                payload = msg.get_payload()

                if isinstance(payload, list):
                    payload = payload[0]

                if plugIt.newMail(data, payload):
                    print "Ok", msg['Subject']
                    cox.dele(i+1)
        cox.quit()
    