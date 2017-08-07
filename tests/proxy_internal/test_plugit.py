from _utils import TestBase


import json
import uuid


class TestPlugIt(TestBase):

    @classmethod
    def setup_class(self):
        super(TestPlugIt, self).setup_class()

        from plugit_proxy.plugIt import PlugIt

        self.plugIt = PlugIt('http://0.0.0.0/')

        myself = self

        def _doQuery(url, method='GET', getParmeters=None, postParameters=None, files=None, extraHeaders={}, session={}):
            myself.lastDoQueryCall = {'url': url, 'method': method, 'getParmeters': getParmeters, 'postParameters': postParameters, 'files': files, 'extraHeaders': extraHeaders, 'session': session}

            class DummyResponse():
                def json(self):
                    return myself.plugIt.toReplyJson()

                @property
                def status_code(self):
                    return myself.plugIt.toReplyStatusCode()

                @property
                def headers(self):
                    return myself.plugIt.toReplyHeaders()

                @property
                def content(self):
                    return json.dumps(self.json())

            return DummyResponse()

        self.plugIt.doQuery = _doQuery

    def test_ping(self):

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'data': self.lastDoQueryCall['url'].split('data=', 1)[1]}

        assert(self.plugIt.ping())

        self.plugIt.toReplyStatusCode = lambda: 404

        assert(not self.plugIt.ping())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'data': self.lastDoQueryCall['url'].split('data=', 1)[1] * 2}

        assert(not self.plugIt.ping())

        assert(self.lastDoQueryCall['url'].startswith('ping'))

    def test_check_version(self):

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION, 'protocol': self.plugIt.PI_API_NAME}

        assert(self.plugIt.checkVersion())
        assert(self.lastDoQueryCall['url'] == 'version')

        self.plugIt.toReplyJson = lambda: {'result': 'poney', 'version': self.plugIt.PI_API_VERSION, 'protocol': self.plugIt.PI_API_NAME}
        assert(not self.plugIt.checkVersion())

        self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION * 2, 'protocol': self.plugIt.PI_API_NAME}
        assert(not self.plugIt.checkVersion())

        self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION, 'protocol': self.plugIt.PI_API_NAME * 2}
        assert(not self.plugIt.checkVersion())

        self.plugIt.toReplyStatusCode = lambda: 201
        self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION, 'protocol': self.plugIt.PI_API_NAME}

        assert(not self.plugIt.checkVersion())

    def test_new_mail(self):

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'result': 'Ok'}

        message_id = str(uuid.uuid4())
        message = str(uuid.uuid4())

        assert(self.plugIt.newMail(message_id, message))
        assert(self.lastDoQueryCall['url'] == 'mail')
        assert(self.lastDoQueryCall['postParameters'].get('response_id') == message_id)
        assert(self.lastDoQueryCall['postParameters'].get('message') == message)

        self.plugIt.toReplyStatusCode = lambda: 201
        assert(not self.plugIt.newMail(message_id, message))

    def test_media(self):
        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {}

        media = str(uuid.uuid4())

        data, content_type, cache_control = self.plugIt.getMedia(media)

        assert(data == '{}')
        assert(content_type == 'application/octet-stream')
        assert(self.lastDoQueryCall['url'] == 'media/{}'.format(media))
        assert(not cache_control)

        self.plugIt.toReplyHeaders = lambda: {'content-type': 'test', 'cache-control': 'public, max-age=31536000'}

        data, content_type, cache_control = self.plugIt.getMedia(media)

        assert(data == '{}')
        assert(content_type == 'test')
        assert(cache_control == 'public, max-age=31536000')

        self.plugIt.toReplyStatusCode = lambda: 201
        data, content_type, cache_control = self.plugIt.getMedia(media)
        assert(not data)
        assert(not content_type)

    def test_meta(self):

        k = str(uuid.uuid4())
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {'expire': 'Wed, 21 Oct 2015 07:28:00 GMT'}

        data = self.plugIt.getMeta(path)
        assert(self.lastDoQueryCall['url'] == 'meta/{}'.format(path))
        assert(data['k'] == k)

        # Data should not be cached
        self.plugIt.toReplyJson = lambda: {'k2': k}
        data = self.plugIt.getMeta(path)
        assert(data['k2'] == k)

    def test_meta_fail(self):
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 201
        assert(not self.plugIt.getMeta(path))

    def test_meta_cache(self):

        k = str(uuid.uuid4())
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {}

        # Data should be cached
        data = self.plugIt.getMeta(path)
        self.plugIt.toReplyJson = lambda: {'k2': k}
        data = self.plugIt.getMeta(path)
        assert(data['k'] == k)

    def test_template(self):

        k = str(uuid.uuid4())
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k, 'template_tag': '-'}
        self.plugIt.toReplyHeaders = lambda: {}

        data = json.loads(self.plugIt.getTemplate(path))
        assert(self.lastDoQueryCall['url'] == 'template/{}'.format(path))
        assert(data['k'] == k)

        # Data should be cached
        self.plugIt.toReplyJson = lambda: {'k2': k, 'template_tag': '-'}
        data = json.loads(self.plugIt.getTemplate(path))
        assert(data['k'] == k)

    def test_template_fail(self):

        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 201
        assert(not self.plugIt.getTemplate(path))

    def test_template_no_meta_no_template(self):
        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        assert(not self.plugIt.getTemplate(path))

    def test_do_action_normal_mode(self):

        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {}

        assert(self.plugIt.doAction(path) == ({}, {}, {}))
        assert(self.lastDoQueryCall['url'] == 'action/{}'.format(path))

    def test_do_action_proxy_mode(self):

        path = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {}

        assert(self.plugIt.doAction(path, proxyMode=True) == ("{}", {}, {}))
        assert(self.lastDoQueryCall['url'] == path)

    def test_do_action_proxy_mode_no_remplate(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-notemplate': True}

        r, __, __ = self.plugIt.doAction('', proxyMode=True)

        assert(r.__class__.__name__ == 'PlugItNoTemplate')
        assert(json.loads(r.content)['k'] == k)

    def test_do_action_data(self):

        path = str(uuid.uuid4())
        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {}

        assert(self.plugIt.doAction(path) == ({'k': k}, {}, {}))

    def test_do_action_500(self):
        self.plugIt.toReplyStatusCode = lambda: 500
        assert(self.plugIt.doAction('')[0].__class__.__name__ == 'PlugIt500')

    def test_do_action_fail(self):
        self.plugIt.toReplyStatusCode = lambda: 501
        assert(self.plugIt.doAction('') == (None, {}, {}))

    def test_do_action_special_codes(self):

        special_codes = [429, 404, 403, 401, 304]

        for x in range(200, 500):
            self.plugIt.toReplyStatusCode = lambda: x
            r, __, __ = self.plugIt.doAction('')

            if x in special_codes:
                assert(r.__class__.__name__ == 'PlugItSpecialCode')
                assert(r.code == x)
            else:
                assert(r.__class__.__name__ != 'PlugItSpecialCode')

    def test_do_action_session(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {'Ebuio-PlugIt-SetSession-k': k}
        assert(self.plugIt.doAction('') == ({}, {'k': k}, {}))

    def test_do_action_redirect(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-redirect': k}
        r, session, headers = self.plugIt.doAction('')

        assert(r.__class__.__name__ == 'PlugItRedirect')
        assert(r.url == k)
        assert(not r.no_prefix)
        assert(session == {})
        assert(headers == {})

    def test_do_action_redirect_noprefix(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-redirect': k, 'ebuio-plugit-redirect-noprefix': "True"}
        r, session, headers = self.plugIt.doAction('')

        assert(r.__class__.__name__ == 'PlugItRedirect')
        assert(r.url == k)
        assert(r.no_prefix)
        assert(session == {})
        assert(headers == {})

    def test_do_action_file(self):

        k = str(uuid.uuid4())
        content_type = str(uuid.uuid4())
        content_disposition = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {'k': k}
        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-itafile': k, 'Content-Type': content_type}
        r, session, headers = self.plugIt.doAction('')

        assert(r.__class__.__name__ == 'PlugItFile')
        assert(json.loads(r.content)['k'] == k)
        assert(r.content_type == content_type)
        assert(r.content_disposition == '')
        assert(session == {})
        assert(headers == {})

        self.plugIt.toReplyHeaders = lambda: {'ebuio-plugit-itafile': k, 'Content-Type': content_type, 'content-disposition': content_disposition}
        r, __, __ = self.plugIt.doAction('')
        assert(r.content_disposition == content_disposition)

    def test_do_action_etag(self):

        k = str(uuid.uuid4())

        self.plugIt.toReplyStatusCode = lambda: 200
        self.plugIt.toReplyJson = lambda: {}
        self.plugIt.toReplyHeaders = lambda: {'ETag': k}
        r, session, headers = self.plugIt.doAction('')

        assert(headers == {'ETag': k})
