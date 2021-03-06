from flask import abort, Response
import werkzeug


import sys
sys.path.append('../../../')


import time


from plugit.utils import action, cache, only_logged_user, only_member_user, only_admin_user, only_orga_member_user, only_orga_admin_user, user_info, json_only, no_template, PlugItRedirect, PlugItSendFile, PlugItSetSession, get_session_from_request, xml_only, public, address_in_networks, send_etag, crossdomain


@action(route="/", template="home.html")
def home(request):
    return {'home': '123'}


@action(route='/only_logged_user', template="home.html")
@only_logged_user()
def test_only_logged_user(request):
    return {}


@action(route='/only_member_user', template="home.html")
@only_member_user()
def test_only_member_user(request):
    return {}


@action(route='/only_admin_user', template="home.html")
@only_admin_user()
def test_only_admin_user(request):
    return {}


@action(route='/only_orga_member_user', template="home.html")
@only_orga_member_user()
def test_only_orga_member_user(request):
    return {}


@action(route='/only_orga_admin_user', template="home.html")
@only_orga_admin_user()
def test_only_orga_admin_user(request):
    return {}


@action(route='/cache', template="home.html")
@cache(time=42, byUser=False)
def test_cache(request):
    return {}


@action(route='/cache2', template="home.html")
@cache(time=48, byUser=True)
def test_cache2(request):
    return {}


@action(route='/cacheTime', template="echo.html")
@cache(time=3600, byUser=False)
def test_cache_time(request):
    return {'echo': time.time()}


@action(route='/cacheTime2', template="echo.html")
@cache(time=3600, byUser=True)
def test_cache_time2(request):
    return {'echo': time.time()}


@action(route='/user_info', template="home.html")
@user_info(['1', 'coucou', 3, 'thegame'])
def test_user_info(request):
    return {}


@action(route='/user_pk', template="echo.html")
@user_info(['pk'])
def test_user_pk(request):
    return {'echo': request.args.get('ebuio_u_pk')}


@action(route='/generate_500', template="home.html")
@user_info(['pk'])
def test_500(request):
    a = 1 / 0
    return {}


@action(route='/json_only', template="home.html")
@json_only()
def test_json_only(request):
    return {}


@action(route='/xml_only', template="home.html")
@xml_only()
def test_xml_only(request):
    return {'xml': '<a></a>'}


@action(route='/public', template="home.html")
@public()
def test_public(request):
    return {}


@action(route='/address_in_networks', template="home.html")
@address_in_networks(['127.0.0.1/24'])
def test_address_in_networks(request):
    return {}


@action(route='/address_in_networks_outside', template="home.html")
@address_in_networks(['255.255.255.255/32'])
def test_address_in_networks_outside(request):
    return {}


@action(route='/no_template', template="home.html")
@no_template()
def test_no_template(request):
    return {}


@action(route='/plugitredirect')
def test_plugitredirect(request):

    return PlugItRedirect('/redire_ect')


@action(route='/plugitredirect2')
def test_plugitredirect2(request):

    return PlugItRedirect('/redire_ec2t', no_prefix=True)


@action(route='/external_plugitredirect')
def test_external_plugitredirect(request):
    return PlugItRedirect('redirected')


@action(route='/external_plugitredirect2')
def test_external_plugitredirect2(request):
    return PlugItRedirect('http://127.0.0.1:23423/plugIt/redirected', no_prefix=True)


@action(route='/redirected', template="echo.html")
@no_template()
def test_redirected(request):
    return {'echo': 'redirected'}


@action(route='/plugitsendfile')
def test_plugitsendfile(request):

    return PlugItSendFile('media/testfile2', '123-mine-type')


@action(route='/plugitsendfile2')
def test_plugitsendfile2(request):

    return PlugItSendFile('media/testfile2', '123-mine-type', True, '41-file-name')


@action(route='/plugitsetsession')
def test_plugitsetsession(request):
    return PlugItSetSession({'b': '2'}, {'a': '1'})


@action(route='/plugitsetsession_set_time', template='echo.html')
@no_template()
def test_plugitsetsession_set_time(request):
    t = time.time()
    return PlugItSetSession({'echo': t}, {'t': t})


@action(route='/plugitsetsession_get_time', template='echo.html')
@no_template()
def test_plugitsetsession_get_time(request):
    return {'echo': get_session_from_request(request).get('t')}


@action(route='/csrf_token', template="csrf.html")
@no_template()
def test_csrf_token(request):
    return {}


@action(route='/postonly', methods=['POST'], template="home.html")
def test_postonly(request):

    if request.form.get('1') == '9':
        return {"result": "ok"}


@action(route='/sendfile', methods=['POST'], template="home.html")
def test_sendfile(request):

    if request.files['testfile2'] and request.files['testfile2'].stream.read().strip() == "This is test file 2 !":
        return {"result": "ok"}


@action(route='/sendfile_external', methods=['POST'], template="echo.html")
@no_template()
def test_sendfile_external(request):

    if request.files['testfile2'] and request.files['testfile2'].stream.read().strip() == "This is test file 2 !":
        return {"echo": "ok"}
    return {"echo": "err"}


@action(route='/test_main', template="echo.html")
@no_template()
def test_main(request):
    return {"echo": "ok"}


@action(route='/test_set_user', template="echo.html")
@user_info(['pk'])
@no_template()
def test_set_user(request):
    return {'echo': request.args.get('ebuio_u_pk')}


@action(route='/test_get_orga', template="get_orga.html")
@no_template()
def test_get_orga(request):
    return {}


@action(route='/remote_addr', template="echo.html")
def test_remote_addr(request):
    return {'echo': request.headers.get('X-Plugit-Remote-Addr')}


@action(route='/generate_401', template="echo.html")
def test_generate_401(request):
    abort(401)


@action(route='/generate_403', template="echo.html")
def test_generate_403(request):
    abort(403)


@action(route='/generate_404', template="echo.html")
def test_generate_404(request):
    abort(404)


@action(route='/generate_304', template="echo.html")
def test_generate_304(request):

    class NotModified(werkzeug.exceptions.HTTPException):
        code = 304

        def get_response(self, environment):
            return Response(status=304)

    abort(NotModified())


@action(route='/generate_429', template="echo.html")
def test_generate_429(request):
    abort(429)


@action(route='/etag', template="echo.html")
@send_etag()
def test_etag(request):
    return {'_plugit_etag': 'this-is-an-etag', 'echo': '42'}


@action(route='/if_none_match', template="echo.html")
def test_if_none_match(request):
    return {'echo': request.headers.get('X-PlugIt-If-None-Match')}


@action(route='/crossdomain', template="echo.html")
@crossdomain(origin='test')
def test_cross_domain(request):
    return {'echo': request.headers.get('X-PlugIt-Origin')}
