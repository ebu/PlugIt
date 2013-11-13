PlugIT
======

PlugIt is a framework enhancing the portability and integration of web services requiring a user interface.

We use this framework at EBU to access web services on the EBU.io platform.

***This is a draft of the protocol and implementation. Except issues (and report them) !***

## License

Copyright (c) 2013 EBU. All rights reserved.

The project plugit has been created by the EBU. It consists of software that dynamically links to different existing open source code repositories. It does not incorporate or combines components through copying them (or parts) into the target application and producing a merged object file that is a stand-alone executable. The plugit code and documentation is made available by the EBU on the https://github.com/ebu/PlugIt website, under the terms and conditions of the EUPL (European Union Public Licence) v. 1.1

### Latest version of EUPL

The EUPL licence v1.1 is available in 22 languages: 22-07-2013, https://joinup.ec.europa.eu/software/page/eupl/licence-eupl
Whenever a newer version is officially adopted, that version shall apply, and in case of doubt, the English version shall prevail.

### Exceptions

Contact the EBU (Michael Barroco, barroco@ebu.ch) if you are in need of special licence terms/ distribution rights different from the EU Public Licence.

### Disclaimer

For the avoidance of doubt, and in addition to Articles 7 and 8 of the EUPL, this software is provided 'as-is', without any express or implied warranty. In no event will the EBU or the authors be held liable for any damages arising from the use of this software. Furthermore the EBU cannot be held responsible for any use by third parties using the software, for example with a view to produce / manipulate illegal content or not paying for the use of licensed codec's or any other illegal use.

## Project lead

* Michael Barroco [@barroco](https://github.com/barroco)

## Core contributors

* Maximilien Cuony [@the-glu](https://github.com/the-glu)

## Deps

(`pip install ...`)

* django==1.5.1
* flask
* requests
* python-dateutil
* poster
* python-crypto

## Django client

This repository contains an hors-de-la-boite django application to access a PlugIt server. No setup should be needed (django has to be installed however).

Use `cd Simple Django client` and `python manage.py runserver` to run the project. The interface is available at http://127.0.0.1:8000/

It's possible to change the default location of the PlugIt server (_http://127.0.0.1:5000_) in the app/settings.py file.

## Flask server

The flask server implement a PlugIt server.

server.py is the main flask file, providing different call to the framework, generated from actions defined in actions.py. Basic configuration is available at the beginning of the file. Otherwise, this file **should not be edited** !

Use `cd Simple Flask server`and `python server.py` to run the server.

### Available option
* `DEBUG` : Boolean. Set to True to active flask debugging
* `PI_META_CACHE` : Number of seconds to ask the EBUio server to cache the meta information. Set by default to 0 if _DEBUG_ is True, 5 minutes if _DEBUG_ is False.
* `PI_BASE_URL` : String. The base URL to access the PlugIt API. It's possible to use a different URL (eg. '/plugIt/') to have others flask methods for another API using the same server.py. *Must end with a /*
* `PI_ALLOWED_NETWORKS` : Array of subnets. PlugIt call will be restricted to thoses networks. Eg: `['127.0.0.1/32']` (Single ip), `['0.0.0.0/0']` (Everyone), `['192.168.42.0/24']` (Everyone with ip 192.168.42.X)
* `PI_API_USERDATA` : Array of string. Properties allowed about the current user
* `PI_API_ORGAMODE` : If true, work in Orga mode (next section)
* `PI_API_REALUSERS` : If true, work with real users. Exclusiv with PIAPI_ORGAMODE (don't active both !). You need to setup a database and use `python manage.py syncdb` to create it. Administration is available @ _http://127.0.0.1:8000/admin/_

### OrgaMode

In this mode, the system works with a current organization. For each request an ebuio_orgapk, with the unique ID of the current organization is send.

The user can change the organization based on his list of organizations. It's possible to restrict access using only_orga_member_user and only_orga_admin_user.

only_*_user are for the current project, only_orga_*_user for the current organization.

### actions.py
The user can implement his actions in the actions.py file. Each action is a defined like this

```
@action(route="/test", template="test.html")
def test(request):
    return {"hello": "Test", "data": request.args.get('data', '')}</code>
```

It's possible to use various additional decorators to specify how the meta about the action is generated:

* `@only_logged_user()`: Make action available only for logged users
* `@only_member_user()`: Make action available only for members users
* `@only_admin_user()`: Make action available only for admins users
* `@only_orga_member_user()`: Make action available only for members of the current orga
* `@only_orga_admin_user()`: Make action available only for admins of the current orga
* `@cache(time=0, byUser=None)`: Specify how and how long the action should be cached
* `@user_info(props=[])`: Specify the list of properties requested about the user
* `@json_only`: Specify the action return only json 
* `@no_template`: Specify no master template should be used

Again, the server.py file take care of responding to /meta/, /template/ and /action/ call. The function in actions.py will be called when needed. The request is passed as the first parameters to actions.

To redirect the user, you can use the object PlugItRedirect in utils: `return PlugItRedirect("/action")` or `return PlugItRedirect("http://google.ch", no_prefix=True)

### media/
The media folder contains all media files

### templates/
The template folder contains all templates


# Templates
Each template can extend the template _plugIt/base.html_. The template integrates basic JavaScript and CSS libraries such as jQuery, Bootstrap and integrate into the generic EBUio interface.

Templates use the django templating language. The documentation is available at https://docs.djangoproject.com/en/1.5/topics/templates/

An _ebuio_u_ object is provided, with the current user.

A _ebuio_baseUrl_ value is provided, with the root URL to use for all URL generation (others actions, medias, etc..)

You can use the template tag `plugitInclude` in the library `plugit_tags` to include another template inside a template. The argument to plugItInclude must be an action. The action won't be called but his template will be used. The context is preserved.

You can use the template tag `plugitGetUser` in the library `plugit_tags` to load information about an user using his pk. Example: `{% plugitGetUser media.user_id as tmpuser %}{{tmpuser.username}}`

# API Methods

Each method returns a JSON object, except for /template/ and /media/ calls.

If you use our Flask server, those method are automatically implemented !

## Basic methods

### /ping [data=OptionalData]
/ping is used to test access to the application. The server must reply with an HTTP 200 response and the object {data: _OptionalData_} if everything is ok. The _OptionalData_ must be returned if provided, as send by the client or with a blank string if the parameter wasn't set.

### /version
/version is used to get the current version of the server API. The server must reply with an HTTP 200 response and the object {result: 'Ok', version: '1', protocol: 'EBUio-PlugIt'}, for the current version, if everything is ok.

### /mail
/mail is used by the PlugIt client to send back to the server mails reply from users. He will send back, using a POST request the response_id provided with the API call to send the mail. 

## Actions' methods
The project can define multiples actions, and they are triggered from the templates. There is no definition of the available actions.
The default action, called when the user arrive on the project page on EBUio is defined by a blank string. (root)

### /meta/_action_
This call returns information about a specific action. The server must reply with an HTTP 200 response (or a 404 if the action doesn't exist) with an object. Properties of this object are:

* template_tag : String. The current version of the template. This value must change if the template associated with the action change.
* json_only : Boolean. Optional, default to False. If set to True, return the json directly to the browser, without using a template.
* no_template : Boolean. Optional, default to False. If set to True, return the template directly to the browser, without using a master template.
* only_logged_user : Boolean. Optional, default to False. True if the user must be authenticated on EBUio to call the action.
* only_member_user : Boolean. Optional, default to False.  True if the user must be in the project group on EBUio to call the action.
* only_admin_user : Boolean. Optional, default to False.  True if the user must be an administrator of the project on EBUio to call the action.
* cache_time : Integer. Optional, default to 0. Time, in seconds, on how long the page should be cached on the EBUio side.
* cache_by_user : Boolean. Optional, default to _only_logged_user_ parameter. Set to true if the page must be cached by user. Useful if the page change based on the current user.
* user_info : List of string. Optional, default to []. List of user properties EBUio add to each request. Example properties, the full list isn't defined yet: username, email, first_name, last_name. NB: It's also possible to access this using the API.

The server should set the Expire: _Date_ HTTP header. EBIio will cache the result of the called based on this header. If this header isn't set, a timeout of 5 minutes will be used.

### /template/_action_
This call returns the template for a specific action (no JSON !). 200 HTTP status code must be used if everything is ok, or an HTTP 404 if the action doesn't exist.

### /action/_action_
This call execute on the server the specific action. If a POST method is used on the EBOio side, the request is done to the server using the same method, otherwise using GET.

POST data and URLs parameters are forwarded to the server side, including files, but parameters begging by ebuio_ are removed.

EBUio add to parameters (Using GET or POST data, depending of the method of the request) each parameter requested about the user in ebuio_u_<parameterName> parameters. One should be careful about lengths of those requests.

The server should reply with an HTTP 200 status code (or 404 if the action doesn't exist, 403 if the user hasn't right to call the action). The returned JSON object is forwarded to the template.

It's possible to redirect the client using the header `EbuIo-PlugIt-Redirect`. PlugIt automaticaly append the _ebuio_baseUrl_. To avoid this, set the header `EbuIo-PlugIt-Redirect-NoPrefix` to `True`.

It's possible to send a file using the header `EbuIo-PlugIt-ItAFile`. The content is send to the user, using the same content-type. If any, the Content-Disposition header is also forwarder.

### /media/_medianame_
This call return a specific media on the server side. Each request on EBUio side on /media/* is forwarded to the server and returned to the client. No caching is used, but a 1 hour Cache-Control header is set by EBUio-

## API

The API is available at /plugIt/ebuio_api/ . See the API root page using your browser for details.

A small python class (PlugItAPI) is available in plugit_api.py, methods are also detailled on the API root page.

### Mails

It's possible to send mail using the API. All users reply to the mail, if keeping the same subject and send will a response_id will be send back to the PlugIt server using the /mail call. The response_id is secured in the subject and can be trusted (users cannot generate generic response_id).

The management task check_mail is used to check mails and should be runned inside a cron job on the PlugIt client. Relevent configuration (`INCOMING_MAIL` and `EBUIO_SENDER`) should also be correct.
