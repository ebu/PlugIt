"""Tools to access the PlugIt API"""

import requests
import warnings


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""
    def new_func(*args, **kwargs):
        warnings.warn("Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning)
        return func(*args, **kwargs)
    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func


class PlugItAPI(object):
    """Main instance to access plugit api"""

    def __init__(self, url):
        """Create a new PlugItAPI instance, need url as the main endpoint for the API"""
        self.url = url

    def _request(self, uri, params=None, postParams=None, verb='GET'):
        """Execute a request on the plugit api"""
        return getattr(requests, verb.lower())(self.url + uri, params=params, data=postParams, stream=True)

    def get_user(self, userPk):
        """Returns the user specified with the user's Pk or UUID"""
        r = self._request('user/' + str(userPk))
        if r:
            # Set base properties and copy data inside the user
            u = User()
            u.pk = u.id = userPk
            u.__dict__.update(r.json())
            return u
        return None

    def get_subscription_labels(self, userPk):
        """Returns a list with all the labels the user is subscribed to"""
        r = self._request('subscriptions/' + str(userPk))
        if r:
            s = r.json()
            return s
        return []

    def get_orgas(self):
        """Return the list of pk for all orgas"""

        r = self._request('orgas/')
        if not r:
            return None

        retour = []

        for data in r.json()['data']:
            o = Orga()
            o.__dict__.update(data)
            o.pk = o.id

            retour.append(o)

        return retour

    def get_orga(self, orgaPk):
        """Return an organization speficied with orgaPk"""
        r = self._request('orga/' + str(orgaPk))
        if r:
            # Set base properties and copy data inside the orga
            o = Orga()
            o.pk = o.id = orgaPk
            o.__dict__.update(r.json())
            return o
        return None

    def get_project_members(self):
        """Return the list of members in the project"""

        r = self._request('members/')
        if not r:
            return None

        retour = []

        for data in r.json()['members']:
            # Base properties
            u = User()
            u.__dict__.update(data)

            retour.append(u)

        return retour

    def send_mail(self, sender, subject, recipients, message, response_id=None, html_message=False):
        """Send an email using EBUio features. If response_id is set, replies will be send back to the PlugIt server."""

        params = {
            'sender': sender,
            'subject': subject,
            'dests': recipients,
            'message': message,
            'html_message': html_message,
        }

        if response_id:
            params['response_id'] = response_id

        return self._request('mail/', postParams=params, verb='POST')

    @deprecated
    def ebuio_forum(self, subject, author, message, tags=''):
        return self.forum_create_topic(subject, author, message, tags).json()

    def forum_create_topic(self, subject, author, message, tags=""):
        """Create a topic using EBUio features."""

        params = {'subject': subject, 'author': author, 'message': message, 'tags': tags}

        return self._request('ebuio/forum/', postParams=params, verb='POST')

    def forum_topic_get_by_tag_for_user(self, tag=None, author=None):
        """Get all forum topics with a specific tag"""

        if not tag:
            return None

        if author:
            r = self._request('ebuio/forum/search/bytag/' + tag + '?u=' + author)
        else:
            r = self._request('ebuio/forum/search/bytag/' + tag)
        if not r:
            return None

        retour = []

        for data in r.json().get('data', []):
            retour.append(data)

        return retour


class User(object):
    """Represent an user"""


class Orga(object):
    """Represent an organization"""
