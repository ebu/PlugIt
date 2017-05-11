from hashlib import sha1
import re
import hmac
import binascii


from django.conf import settings


def create_secret(*args, **kwargs):
    """Return a secure key generated from the user and the object. As we load elements fron any class from user imput, this prevent the user to specify arbitrary class"""

    to_sign = '-!'.join(args) + '$$'.join(kwargs.values())

    key = settings.SECRET_FOR_SIGNS

    hashed = hmac.new(key, to_sign, sha1)
    return re.sub(r'[\W_]+', '', binascii.b2a_base64(hashed.digest()))
