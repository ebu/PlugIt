from test_proxyviews import TestProxyViews


class TestProxyViewsAccess(TestProxyViews):

    def batch_check_rights_and_access(self, request, meta, rights):

        for right, value in rights.items():
            request.user = self.views.generate_user(right)
            response = self.views.check_rights_and_access(request, meta)

            if value:
                if not response or response.status_code != value:
                    print("Excepted {}, got {}".format(value, response.status_code if response else 'Nothing'))
                    assert(False)
            else:
                if response:
                    print("Excepted nothing, got {}".format(response.status_code if response else 'Nothing'))
                    assert(False)

    def test_rights_and_access_nothing_needed(self):

        self.batch_check_rights_and_access(self.build_request('/'), {}, {
            'ano': False,
            'log': False,
            'mem': False,
            'adm': False,
        })

    def test_check_rights_and_access_logged_in(self):

        meta = {'only_logged_user': True}

        self.batch_check_rights_and_access(self.build_request('/'), meta, {
            'ano': 403,
            'log': False,
            'mem': False,
            'adm': False,
        })

    def test_check_rights_and_access_member(self):

        meta = {'only_member_user': True}

        self.batch_check_rights_and_access(self.build_request('/'), meta, {
            'ano': 403,
            'log': 403,
            'mem': False,
            'adm': False,
        })

    def test_check_rights_and_access_admin(self):

        meta = {'only_admin_user': True}

        self.batch_check_rights_and_access(self.build_request('/'), meta, {
            'ano': 403,
            'log': 403,
            'mem': 403,
            'adm': False,
        })

    def test_check_rights_and_access_orga_member(self):

        meta = {'only_orga_member_user': True}

        self.batch_check_rights_and_access(self.build_request('/'), meta, {
            'ano': 403,
            'log': 403,
            'mem': False,
            'adm': False,
        })

    def test_check_rights_and_access_orga_admin(self):

        meta = {'only_orga_admin_user': True}

        self.batch_check_rights_and_access(self.build_request('/'), meta, {
            'ano': 403,
            'log': 403,
            'mem': 403,
            'adm': False,
        })

    def test_check_rights_and_access_address_in_network(self):

        request = self.build_request('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'

        meta = {'address_in_networks': ['127.0.0.1/32']}

        self.batch_check_rights_and_access(request, meta, {
            'ano': False,
            'log': False,
            'mem': False,
            'adm': False,
        })

        request = self.build_request('/')
        request.META['REMOTE_ADDR'] = '42.42.42.42'

        self.batch_check_rights_and_access(request, meta, {
            'ano': 403,
            'log': 403,
            'mem': 403,
            'adm': 403,
        })

        meta = {'address_in_networks': ['127.0.0.1/32', '42.42.42.0/24']}

        self.batch_check_rights_and_access(request, meta, {
            'ano': False,
            'log': False,
            'mem': False,
            'adm': False,
        })

        request = self.build_request('/')
        request.META['REMOTE_ADDR'] = ''

        self.batch_check_rights_and_access(request, meta, {
            'ano': 403,
            'log': 403,
            'mem': 403,
            'adm': 403,
        })

    def test_address_in_network(self):

        # Test common cases
        assert(self.views.is_address_in_network('127.0.0.1', '127.0.0.1/32'))
        assert(self.views.is_address_in_network('127.0.0.1', '127.0.0.1/24'))
        assert(self.views.is_address_in_network('127.0.0.1', '127.0.0.1/16'))
        assert(self.views.is_address_in_network('127.0.0.1', '127.0.0.1/8'))
        assert(self.views.is_address_in_network('127.0.0.1', '127.0.0.1/0'))

        assert(not self.views.is_address_in_network('127.0.0.2', '127.0.0.1/32'))
        assert(self.views.is_address_in_network('127.0.0.2', '127.0.0.1/24'))
        assert(self.views.is_address_in_network('127.0.0.2', '127.0.0.1/16'))
        assert(self.views.is_address_in_network('127.0.0.2', '127.0.0.1/8'))
        assert(self.views.is_address_in_network('127.0.0.2', '127.0.0.1/0'))

        assert(not self.views.is_address_in_network('127.0.1.1', '127.0.0.1/32'))
        assert(not self.views.is_address_in_network('127.0.1.1', '127.0.0.1/24'))
        assert(self.views.is_address_in_network('127.0.1.1', '127.0.0.1/16'))
        assert(self.views.is_address_in_network('127.0.1.1', '127.0.0.1/8'))
        assert(self.views.is_address_in_network('127.0.1.1', '127.0.0.1/0'))

        assert(not self.views.is_address_in_network('127.1.1.1', '127.0.0.1/32'))
        assert(not self.views.is_address_in_network('127.1.1.1', '127.0.0.1/24'))
        assert(not self.views.is_address_in_network('127.1.1.1', '127.0.0.1/16'))
        assert(self.views.is_address_in_network('127.1.1.1', '127.0.0.1/8'))
        assert(self.views.is_address_in_network('127.1.1.1', '127.0.0.1/0'))

        assert(not self.views.is_address_in_network('128.1.1.1', '127.0.0.1/32'))
        assert(not self.views.is_address_in_network('128.1.1.1', '127.0.0.1/24'))
        assert(not self.views.is_address_in_network('128.1.1.1', '127.0.0.1/16'))
        assert(not self.views.is_address_in_network('128.1.1.1', '127.0.0.1/8'))
        assert(self.views.is_address_in_network('128.1.1.1', '127.0.0.1/0'))
