import sys
sys.path.append('../../../')

from plugit.utils import action, cache, only_logged_user, only_member_user, only_admin_user, only_orga_member_user, only_orga_admin_user, user_info, json_only, no_template, PlugItRedirect, PlugItSendFile, PlugItSetSession


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


@action(route='/user_info', template="home.html")
@user_info(['1', 'coucou', 3, 'thegame'])
def test_user_info(request):
    return {}


@action(route='/json_only', template="home.html")
@json_only()
def test_json_only(request):
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


@action(route='/plugitsendfile')
def test_plugitsendfile(request):

    return PlugItSendFile('media/testfile2', '123-mine-type')


@action(route='/plugitsendfile2')
def test_plugitsendfile2(request):

    return PlugItSendFile('media/testfile2', '123-mine-type', True, '41-file-name')


@action(route='/plugitsetsession')
def test_plugitsetsession(request):

    return PlugItSetSession({'b': '2'}, {'a': '1'})


@action(route='/postonly', methods=['POST'], template="home.html")
def test_postonly(request):

    if request.form.get('1') == '9':
        return {"result": "ok"}


@action(route='/sendfile', methods=['POST'], template="home.html")
def test_sendfile(request):

    if request.files['testfile2'] and request.files['testfile2'].stream.read().strip() == "This is test file 2 !":
        return {"result": "ok"}
