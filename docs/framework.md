PlugIt Framework
====

## Service structure

### Decorators: actions.py
The user can implement his actions in the actions.py file. Each action is a defined like this

```
@action(route="/test", template="test.html")
def test(request):
    return {"hello": "Test", "data": request.args.get('data', '')}
```

It's possible to use various additional decorators to specify how the meta about the action is generated:

* `@only_logged_user()`: Make action available only for logged users
* `@only_member_user()`: Make action available only for members users
* `@only_admin_user()`: Make action available only for admins users
* `@only_orga_member_user()`: Make action available only for members of the current orga
* `@only_orga_admin_user()`: Make action available only for admins of the current orga
* `@cache(time=0, byUser=None)`: Specify how and how long the action should be cached
* `@address_in_networks(networks=['0.0.0.0/0',])` : Specify the networks in which the remote ip must be
* `@user_info(props=[])`: Specify the list of properties requested about the user
* `@json_only`: Specify the action return only json
* `@xml_only`: Specify the action return only xml (Response to have structure {'xml':'..'})
* `@no_template`: Specify no master template should be used

Again, the server.py file take care of responding to /meta/, /template/ and /action/ call. The function in actions.py will be called when needed. The request is passed as the first parameters to actions.

To redirect the user, you can use the object PlugItRedirect in utils: `return PlugItRedirect("/action")` or `return PlugItRedirect("http://google.ch", no_prefix=True)

### media/
The media folder contains all media files

### templates/
The template folder contains all templates


## Templates
Each template can extend the template _plugIt/base.html_. The template integrates basic JavaScript and CSS libraries such as jQuery, Bootstrap and integrate into the generic EBUio interface.

Templates use the django templating language. The documentation is available at https://docs.djangoproject.com/en/1.5/topics/templates/

An _ebuio_u_ object is provided, with the current user.

A _ebuio_baseUrl_ value is provided, with the root URL to use for all URL generation (others actions, medias, etc..)

You can use the template tag `plugitInclude` in the library `plugit_tags` to include another template inside a template. The argument to plugItInclude must be an action. The action won't be called but his template will be used. The context is preserved.

You can use the template tag `plugitGetUser` in the library `plugit_tags` to load information about an user using his pk. Example: `{% plugitGetUser media.user_id as tmpuser %}{{tmpuser.username}}`


## Configuration

### Available options

Settings are defined in the `config.py` file.

* `DEBUG` : Boolean. Set to True to active flask debugging
* `PI_META_CACHE` : Number of seconds to ask the _PlugIt Proxy_ to cache the meta information. Set by default to 0 if _DEBUG_ is True, 5 minutes if `DEBUG` is False.
* `PI_BASE_URL` : String. The base URL to access the PlugIt API. It's possible to use a different URL (eg. '/plugIt/') to have others flask methods for another API using the same server.py. *Must end with a /*
* `PI_ALLOWED_NETWORKS` : Array of subnets. PlugIt call will be restricted to thoses networks. Eg: `['127.0.0.1/32']` (Single ip), `['0.0.0.0/0']` (Everyone), `['192.168.42.0/24']` (Everyone with ip 192.168.42.X)
* `PI_API_USERDATA` : Array of string. Properties allowed about the current user
* `PI_API_ORGAMODE` : If true, work in Orga mode (next section)
* `PI_API_REALUSERS` : If true, work with real users. Exclusive with PIAPI_ORGAMODE (don't active both !). You need to setup a database and use `python manage.py syncdb` to create it. Administration is available @ _http://127.0.0.1:8000/admin/_
* `PIAPI_PLUGITMENUACTION` : the block name in which your application returns the menu and the action name to call to get only the menu back from your application ( see [Service specific Navigation Bar](#service-specific-navigation-bar) )
* `PIAPI_PLUGITTEMPLATE` : the PlugIt Proxy comes with a predefined template which displays a menu. Change this setting to `plugItBase-menu.html`. ( see [Menu Bar](#menu-bar) )


### OrgaMode

In this mode, the system works with a current organization. For each request an ebuio_orgapk, with the unique ID of the current organization is send.

The user can change the organization based on his list of organizations. It's possible to restrict access using only_orga_member_user and only_orga_admin_user.

only_*_user are for the current project, only_orga_*_user for the current organization.


### Service specific Navigation Bar

The PlugIt API allows your application to provide a left hand side menu. In order to use it, you will need to define or 
change a few settings:

    PIAPI_PLUGITMENUACTION = 'menubar'
    PIAPI_PLUGITTEMPLATE = 'plugItBase-menu.html'
    
*`PIAPI_PLUGITMENUACTION` : the block name in which your application returns the menu and the action name to call to get
only the menu back from your application
*'PIAPI_PLUGITTEMPLATE' : the PlugIt Proxy comes with a predefined template which displays a menu. Change this setting
to `plugItBase-menu.html`.

### Tags and structure of the navigation bar and page

Your menu should look something like the following code to pick up the predefined CSS styles. Of course you can define
you own.

    <div class="menu-section">
        <h3>Menu Section</h3>
        <ul>
            <li><a href="/plugIt/url1/">My Option 1</a></li>
            <li><a href="/plugIt/url2/">My Option 2</a></li>
            <li><a href="/plugIt/url3/">My Option 3 Provider</a></li>
        </ul>
    </div>
    <div class="menu-section">
            <h3>Another Section</h3>
    ...

If additionally you need a row on top of the pages to contain title and page functions, use the following structure:

    <div class="menubar">
        <div class="page-title">
            Page Title :: Sub Page
            <small class="hidden-xs"> </small>
        </div>
        <div id="page-functions" class="pull-right">
            <button type="button" class="btn btn-default" >
                Button Function
            </button>
            <a href="/plugIt/linktootherpage" class="btn btn-primary">Add a new station</a>
        </div>
    </div>
