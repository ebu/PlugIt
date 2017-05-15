from test_proxyviews import TestProxyViews


import uuid


class TestProxyViewsGenerate(TestProxyViews):

    def test_generate_user_nobody(self):
        assert(not self.views.generate_user(None, None))

    def test_generate_user_ano(self):
        user = self.views.generate_user('ano')
        assert(user)
        assert(not user.is_authenticated())
        assert(not user.ebuio_member)
        assert(not user.ebuio_admin)
        assert(not user.ebuio_orga_member)
        assert(not user.ebuio_orga_admin)

    def test_generate_user_log(self):
        user = self.views.generate_user('log')
        assert(user)
        assert(user.is_authenticated())
        assert(not user.ebuio_member)
        assert(not user.ebuio_admin)
        assert(not user.ebuio_orga_member)
        assert(not user.ebuio_orga_admin)

    def test_generate_user_mem(self):
        user = self.views.generate_user('mem')
        assert(user)
        assert(user.is_authenticated())
        assert(user.ebuio_member)
        assert(not user.ebuio_admin)
        assert(user.ebuio_orga_member)
        assert(not user.ebuio_orga_admin)

    def test_generate_user_adm(self):
        user = self.views.generate_user('adm')
        assert(user)
        assert(user.is_authenticated())
        assert(user.ebuio_member)
        assert(user.ebuio_admin)
        assert(user.ebuio_orga_member)
        assert(user.ebuio_orga_admin)

    def test_generate_user_compat_mode(self):
        user = self.views.generate_user(None, 3)
        assert(user)
        assert(user.is_authenticated())
        assert(not user.ebuio_member)
        assert(not user.ebuio_admin)
        assert(not user.ebuio_orga_member)
        assert(not user.ebuio_orga_admin)

    def test_gen_404(self):
        raison = str(uuid.uuid4())
        url = self.random_base_url()
        usermode = str(uuid.uuid4())

        request = self.build_request('/')
        request.session['plugit-standalone-usermode'] = usermode

        response = self.views.gen404(request, url, raison)

        assert(response)
        assert(response.status_code == 404)
        assert(response.content.strip() == '404,{},{},{}'.format(raison, url, usermode))

        self.restore_base_url()

    def test_gen_500(self):
        url = self.random_base_url()
        usermode = str(uuid.uuid4())

        request = self.build_request('/')
        request.session['plugit-standalone-usermode'] = usermode

        response = self.views.gen500(request, url)

        assert(response)
        assert(response.status_code == 500)
        assert(response.content.strip() == '500,{},{}'.format(url, usermode))

        self.restore_base_url()

    def test_gen_403(self):
        raison = str(uuid.uuid4())
        project = str(uuid.uuid4())
        url = self.random_base_url()
        usermode = str(uuid.uuid4())

        request = self.build_request('/')
        request.session['plugit-standalone-usermode'] = usermode

        response = self.views.gen403(request, url, raison, project)

        assert(response)
        assert(response.status_code == 403)
        assert(response.content.strip() == '403,{},{},{},{}'.format(raison, url, usermode, project))

        self.restore_base_url()

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
