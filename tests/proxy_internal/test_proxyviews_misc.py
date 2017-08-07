from test_proxyviews import TestProxyViews


from django.conf import settings
import json
import uuid


class TestProxyViewsMisc(TestProxyViews):

    def test_build_base_parmeters_get(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.factory.get('/', {'k': k, 'ebuio_k': k2})

        get, post, files = self.views.build_base_parameters(r)

        assert(get['k'] == k)
        assert('ebuio_k' not in get)
        assert(not post)

    def test_build_base_parmeters_get_list(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.factory.get('/', {'k': [k, k2]})

        get, post, files = self.views.build_base_parameters(r)

        assert(get['k'] == [k, k2])

    def test_build_base_parmeters_post(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.factory.post('/', {'k': k, 'ebuio_k': k2})

        get, post, files = self.views.build_base_parameters(r)

        assert(not get)
        assert(post['k'] == k)
        assert('ebuio_k' not in post)

    def test_build_base_parmeters_post_list(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.factory.post('/', {'k': [k, k2]})

        get, post, files = self.views.build_base_parameters(r)

        assert(post['k'] == [k, k2])

    def test_build_base_parmeters_post_and_get(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.factory.post('/?k={}'.format(k), {'k': k2})

        get, post, files = self.views.build_base_parameters(r)

        assert(get['k'] == k)
        assert(post['k'] == k2)

    def test_build_base_parmeters_post_files(self):

        with open('tests/helpers/flask_server/media/testfile1', 'rb') as f:
            r = self.factory.post('/', {'k': f, 'ebuio_k': f})

        get, post, files = self.views.build_base_parameters(r)

        assert(not get)
        assert(not post)
        assert('k' in files)
        assert('ebuio_k' not in files)

    def test_build_user_requested_parameters(self):

        settings.PIAPI_USERDATA = ['k']

        k = str(uuid.uuid4())

        class U():
            pass

        r = self.build_request('/')
        r.user = U()
        r.user.k = k

        get, post, files = self.views.build_user_requested_parameters(r, {'user_info': ['k']})

        assert(get['ebuio_u_k'] == k)
        assert(not post)
        assert(not files)

    def test_build_user_requested_parameters_post(self):

        settings.PIAPI_USERDATA = ['k']

        k = str(uuid.uuid4())

        class U():
            pass

        r = self.factory.post('/')
        r.user = U()
        r.user.k = k

        get, post, files = self.views.build_user_requested_parameters(r, {'user_info': ['k']})

        assert(not get)
        assert(post['ebuio_u_k'] == k)
        assert(not files)

    def test_build_user_requested_parameters_unknown(self):

        settings.PIAPI_USERDATA = []

        k = str(uuid.uuid4())

        class U():
            pass

        r = self.factory.post('/')
        r.user = U()
        r.user.k = k

        # Should raise exception
        try:
            get, post, files = self.views.build_user_requested_parameters(r, {'user_info': ['k']})
        except Exception:
            return

        assert(False)

    def test_build_user_requested_parameters_not_a_prop(self):

        settings.PIAPI_USERDATA = ['k']

        class U():
            pass

        r = self.factory.post('/')
        r.user = U()

        # Should raise exception
        try:
            get, post, files = self.views.build_user_requested_parameters(r, {'user_info': ['k']})
        except Exception:
            return

        assert(False)

    def test_build_user_requested_parameters_prop_false(self):

        settings.PIAPI_USERDATA = ['k']

        class U():
            pass

        r = self.factory.post('/')
        r.user = U()
        r.user.k = None

        get, post, files = self.views.build_user_requested_parameters(r, {'user_info': ['k']})

        assert(not get)
        assert(not post['ebuio_u_k'])
        assert(not files)

    def test_build_orga_parameters_no_orga(self):

        assert(self.views.build_orga_parameters(None, False, False) == ({}, {}, {}))
        assert(self.views.build_orga_parameters(None, True, False) == ({}, {}, {}))
        assert(self.views.build_orga_parameters(None, False, True) == ({}, {}, {}))

    def test_build_orga_parameters_orga(self):

        class O():
            pk = str(uuid.uuid4())

        assert(self.views.build_orga_parameters(self.factory.get('/'), True, O()) == ({'ebuio_orgapk': O.pk}, {}, {}))
        assert(self.views.build_orga_parameters(self.factory.post('/'), True, O()) == ({}, {'ebuio_orgapk': O.pk}, {}))

    def test_build_parameters(self):

        settings.PIAPI_USERDATA = ['k']

        class O():
            pk = str(uuid.uuid4())

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        class U():
            pass

        r = self.factory.get('/', {'k2': k2})
        r.user = U()
        r.user.k = k

        get, post, files = self.views.build_parameters(r, {'user_info': ['k']}, True, O())

        assert(get['ebuio_orgapk'] == O.pk)
        assert(get['k2'] == k2)
        assert(get['ebuio_u_k'] == k)
        assert(not post)
        assert(not files)

    def test_build_extra_headers(self):

        k = str(uuid.uuid4())
        uri = self.random_base_url()
        remote = str(uuid.uuid4())
        if_none_match = str(uuid.uuid4())

        assert(not self.views.build_extra_headers(None, False, False, None))

        settings.PIAPI_USERDATA = ['k']

        class U():
            pass

        r = self.factory.get('/')
        r.user = U()
        r.user.k = k
        r.META = {'REMOTE_ADDR': remote, 'HTTP_IF_NONE_MATCH': if_none_match}

        headers = self.views.build_extra_headers(r, True, False, None)

        assert(headers['user_k'] == k)
        assert(headers['base_url'] == uri)
        assert(headers['remote-addr'] == remote)
        assert(headers['If-None-Match'] == if_none_match)
        assert('orga_pk' not in headers)
        assert('orga_name' not in headers)
        assert('orga_codops' not in headers)

        class O():
            pk = str(uuid.uuid4())
            name = str(uuid.uuid4())
            ebu_codops = str(uuid.uuid4())

        headers = self.views.build_extra_headers(r, True, True, O())
        assert(headers['orga_pk'] == O.pk)
        assert(headers['orga_name'] == O.name)
        assert(headers['orga_codops'] == O.ebu_codops)

        self.restore_base_url()

    def test_handle_special_case_no_data(self):
        assert(self.views.handle_special_cases(self.build_request('/'), None, None, {}).status_code == 404)

    def test_handle_special_case_empty_data(self):
        assert(not self.views.handle_special_cases(self.build_request('/'), {}, None, {}))

    def test_handle_special_case_500(self):

        class PlugIt500():
            pass

        assert(self.views.handle_special_cases(self.build_request('/'), PlugIt500(), None, {}).status_code == 500)

    def test_handle_special_case_redirect(self):

        class PlugItRedirect():
            def __init__(self, url, no_prefix=False):
                self.url = url
                self.no_prefix = no_prefix

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        r = self.views.handle_special_cases(self.build_request('/'), PlugItRedirect(k), k2, {})
        assert(r.status_code == 302)
        assert(r['Location'] == '{}{}'.format(k2, k))

        r = self.views.handle_special_cases(self.build_request('/'), PlugItRedirect(k, True), k2, {})
        assert(r.status_code == 302)
        assert(r['Location'] == k)

    def test_handle_special_case_file(self):

        class PlugItFile():
            content = str(uuid.uuid4())
            content_type = str(uuid.uuid4())
            content_disposition = str(uuid.uuid4())

        r = self.views.handle_special_cases(self.build_request('/'), PlugItFile(), None, {})

        assert(r.content == PlugItFile.content)
        assert(r['Content-Type'] == PlugItFile.content_type)
        assert(r['Content-Disposition'] == PlugItFile.content_disposition)

    def test_handle_special_case_no_template(self):

        class PlugItNoTemplate():
            content = str(uuid.uuid4())

        r = self.views.handle_special_cases(self.build_request('/'), PlugItNoTemplate(), None, {})

        assert(r.content == PlugItNoTemplate.content)

    def test_handle_special_case_json_1(self):

        k = str(uuid.uuid4())

        r = self.views.handle_special_cases(self.build_request('/'), {'k': k}, None, {'json_only': True})

        assert(r.content == json.dumps({'k': k}))
        assert('json' not in r['Content-Type'])

    def test_handle_special_case_json_2(self):

        k = str(uuid.uuid4())

        request = self.build_request('/')
        request.META['HTTP_ACCEPT'] = 'text/json'

        r = self.views.handle_special_cases(request, {'k': k}, None, {'json_only': True})

        assert(r.content == json.dumps({'k': k}))
        assert('json' in r['Content-Type'])

    def test_handle_special_case_xml(self):

        k = str(uuid.uuid4())

        r = self.views.handle_special_cases(self.build_request('/'), {'xml': k}, None, {'xml_only': True})

        assert(r.content == k)

    def test_build_final_template_no_template(self):

        k = str(uuid.uuid4())

        assert(self.views.build_final_response(None, {'no_template': True}, k, None, None, None, None).content == k)

    def test_build_final_template_proxy(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())
        k3 = str(uuid.uuid4())

        assert(self.views.build_final_response(self.build_request('/'), {}, k, k2, None, True, k3).content.strip() == "base,{},{},{}".format(k, k2, k3))

    def test_build_final_template(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())
        k3 = str(uuid.uuid4())

        assert(self.views.build_final_response(self.build_request('/'), {}, k, k2, None, False, k3).content.strip() == "plugitbase,{},{},{}".format(k, k2, k3))

    def test_render_data_proxy(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        tpl = "{}{}~__PLUGIT_CSRF_TOKEN__~{}".format(k, "{", "}")

        assert(self.views.render_data({'csrf_token': k2}, None, True, tpl) == ("{}{}".format(k, k2), None))

    def test_render_data(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())
        menu = str(uuid.uuid4())

        tpl = "{}{}k2{}{}% block menubar %{}menu{}% endblock %{}".format(k, "{{", "}}", "{", "}{{", "}}{", "}")

        assert(self.views.render_data(self.views.Context({'k2': k2, 'menu': menu}), tpl, False, None) == ("{}{}{}".format(k, k2, menu), menu))

    def test_build_context(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())
        k3 = str(uuid.uuid4())
        url = self.random_base_url()

        class U:
            pk = str(uuid.uuid4())

        request = self.build_request('/')
        request.session['plugit-standalone-usermode'] = k
        request.user = U()

        result = self.views.build_context(request, {'k2': k2}, None, False, None, None)

        assert(result['ebuio_baseUrl'] == url)
        assert(result['ebuio_u'].id == U.pk)
        assert(result['ebuio_u'].pk == U.pk)
        assert(result['ebuio_userMode'] == k)
        assert(not result['ebuio_realUsers'])
        assert(not result['ebuio_orgamode'])
        assert(result['k2'] == k2)
        assert('csrf_token' in result)
        assert('MEDIA_URL' in result)
        assert('STATIC_URL' in result)

        result = self.views.build_context(request, {'k2': k2}, None, True, k3, None)
        assert(result['ebuio_orgamode'])
        assert(result['ebuio_orga'] == k3)

        self.restore_base_url()

    def test_get_template_proxy(self):
        assert(self.views.get_template(None, None, None, True) == (None, None))

    def test_get_template(self):
        request = self.build_request('/')
        assert(self.views.get_template(request, "", {}, False) == ('home_template\n', None))

    def test_get_template_404(self):
        request = self.build_request('/')
        template, exception = self.views.get_template(request, "_", {}, False)

        assert(not template)
        assert(exception)
        assert(exception.status_code == 404)

    def test_session(self):

        k = str(uuid.uuid4())
        k2 = str(uuid.uuid4())

        request = self.build_request('/')

        self.views.update_session(request, {'k': k}, 1)
        retour = self.views.get_current_session(request, 1)
        assert(retour.get('k') == k)

        self.views.update_session(request, {'k': k2}, 2)
        retour = self.views.get_current_session(request, 1)
        assert(retour.get('k') == k)
        retour = self.views.get_current_session(request, 2)
        assert(retour.get('k') == k2)
