from test_proxyviews import TestProxyViews


import uuid


class TestProxyViewsCache(TestProxyViews):

    def test_cache_key_no_cache(self):
        assert(not self.views.get_cache_key(None, {}, None, None))

    def test_cache_key_zero_cache_time(self):
        assert(not self.views.get_cache_key(None, {'cache_time': 0}, None, None))

    def test_cache_key_cache_time(self):
        assert(self.views.get_cache_key(self.build_request('/'), {'cache_time': 1, 'template_tag': ''}, None, None))

    def test_cache_key_varies_on_path(self):
        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        headers = {'cache_time': 1, 'template_tag': ''}

        assert(self.views.get_cache_key(self.build_request(k), headers, None, None) == self.views.get_cache_key(self.build_request(k), headers, None, None))
        assert(self.views.get_cache_key(self.build_request(k), headers, None, None) != self.views.get_cache_key(self.build_request(k2), headers, None, None))

    def test_cache_key_varies_on_template_tag(self):
        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        request = self.build_request('/')

        assert(self.views.get_cache_key(request, {'cache_time': 1, 'template_tag': k}, None, None) == self.views.get_cache_key(request, {'cache_time': 1, 'template_tag': k}, None, None))
        assert(self.views.get_cache_key(request, {'cache_time': 1, 'template_tag': k}, None, None) != self.views.get_cache_key(request, {'cache_time': 1, 'template_tag': k2}, None, None))

    def test_cache_key_varies_on_orga(self):

        class O1:
            pk = str(uuid.uuid4())

        class O2:
            pk = str(uuid.uuid4())

        headers = {'cache_time': 1, 'template_tag': ''}
        request = self.build_request('/')

        assert(self.views.get_cache_key(request, headers, False, O1) == self.views.get_cache_key(request, headers, False, O1))
        assert(self.views.get_cache_key(request, headers, False, O1) == self.views.get_cache_key(request, headers, False, O2))
        assert(self.views.get_cache_key(request, headers, True, O1) == self.views.get_cache_key(request, headers, True, O1))
        assert(self.views.get_cache_key(request, headers, True, O1) != self.views.get_cache_key(request, headers, True, O2))

    def test_cache_key_varies_on_user(self):

        class U1:
            pk = str(uuid.uuid4())

        class U2:
            pk = str(uuid.uuid4())

        r1 = self.build_request('/')
        r2 = self.build_request('/')

        r1.user = U1()
        r2.user = U2()

        headers = {'cache_time': 1, 'template_tag': ''}

        assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r1, headers, False, False))
        assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r2, headers, False, False))

        headers = {'cache_time': 1, 'template_tag': '', 'cache_by_user': False}

        assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r1, headers, False, False))
        assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r2, headers, False, False))

        headers = {'cache_time': 1, 'template_tag': '', 'cache_by_user': True}

        assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r1, headers, False, False))
        assert(self.views.get_cache_key(r1, headers, False, False) != self.views.get_cache_key(r2, headers, False, False))

        for should_cache in ['only_logged_user', 'only_member_user', 'only_admin_user', 'only_orga_member_user', 'only_orga_admin_user']:
            headers = {'cache_time': 1, 'template_tag': '', should_cache: True}

            assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r1, headers, False, False))
            assert(self.views.get_cache_key(r1, headers, False, False) != self.views.get_cache_key(r2, headers, False, False))

            headers = {'cache_time': 1, 'template_tag': '', 'cache_by_user': False, should_cache: True}

            assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r1, headers, False, False))
            assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r2, headers, False, False))

            headers = {'cache_time': 1, 'template_tag': '', 'cache_by_user': True, should_cache: True}

            assert(self.views.get_cache_key(r1, headers, False, False) == self.views.get_cache_key(r1, headers, False, False))
            assert(self.views.get_cache_key(r1, headers, False, False) != self.views.get_cache_key(r2, headers, False, False))

    def test_caching(self):

        cache_key = str(uuid.uuid4())
        result = {'r': uuid.uuid4()}
        menu = {'r': uuid.uuid4()}

        class Context():
            dicts = [{'r': uuid.uuid4(), 'csrf_token': uuid.uuid4()}]

        meta = {'cache_time': 1}

        self.views.cache_if_needed(cache_key, result, menu, Context(), meta)

        r, m, c = self.views.find_in_cache(cache_key)

        assert(r == result)
        assert(m == menu)
        assert(c['r'] == Context.dicts[0]['r'])
        assert('csrf_token' not in c)

        # Unknows keys shouldn't be cached
        r, m, c = self.views.find_in_cache(cache_key * 2)
        assert(not r)
        assert(not m)
        assert(not c)

        # No key, no cache
        r, m, c = self.views.find_in_cache(None)
        assert(not r)
        assert(not m)
        assert(not c)

        # Caching should works without a menu
        self.views.cache_if_needed(cache_key, result, None, Context(), meta)

        r, m, c = self.views.find_in_cache(cache_key)
        assert(r)
        assert(not m)
        assert(c)
