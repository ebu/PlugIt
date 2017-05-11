PlugIT: Tests
=============

Tests exists to be able to test the PlugIt system, for client side and for server side.

nose is used and can be installed using `pip install nose`.

# Run tests

Just go into the PlugIt folder and run `nosetests tests`

# Architecture

The goal is to cover all functionalities. Tests are separated in 4 files:

## proxy_external.py

This file contains tests for the PlugIt proxy, using external HTTP call to the web server. A simple plugit service is run behind the PlugIt proxy.

## proxy_internal.py

This file contains tests for the PlugIt proxy, testing internal python calls.

Tests are subdivided into different classes.

### TestCheckMail

Test the management command _check_mail.py_. A helper simulate a pop server to provide incoming mails.

### TestPlugItTags

Test the PlugIt template tags, using small templates fragments.

### TestPlugItDoQueryTest

Test the _doQuery_ function in the plugIt.py file. Others tests for the _plugIt.py_ file is in another test class, rewriting the _doQuery_ function.

### TestPlugIt

Test functions (except _doQuery_) in the _plugIt.py_ file. _doQuery_ function is rewriten to simulate corrects (or incorrets) replies from a PlugIt server.

Tests can modify functions to set elements returned by the _doQuery_ function. Parameters for the doQuery function's call are saved into the _lastDoQueryCall_ propery of the test class.

Example:

```
self.plugIt.toReplyStatusCode = lambda: 200
self.plugIt.toReplyJson = lambda: {'result': 'Ok', 'version': self.plugIt.PI_API_VERSION, 'protocol': self.plugIt.PI_API_NAME}

assert(self.plugIt.checkVersion())
assert(self.lastDoQueryCall['url'] == 'version')
```

### TestPlugItViews

Tests views in `views.py`, using direct calls and 'false' requests created with django testing utils.

Some helpers functions are also tested.

API views aren't tested yet.

## service_external.py

This file contains tests for the PlugIt simple service, using HTTP calls to the PlugIt server.

A a simple service, using plugIt example, return well-knowns values for differents calls.

There is only one class for tests, _TestExternal_.

## service_internal.py

This file contains tests for the PlugIt service, testing internal python functions.

Tests are subdivied in multiples classes.

### TestUtils

Test the _utils.py_ file.

### TestViews

Test the _views.py_ file. Tests use the `patch_view` function to allow simulation of direct calls without a web context: the flask _Request_ object is replaced with a simple dummy class and some function are rewriten to simple ones.

### TestApi

Test the _api.py_ file. A simple flask server is used to simulate a API server, but returning well-knows values for differents calls. Thoses values are passed as parameters for the server, at launch.
# Helpers

To tests diffrents parts of the system, we use some external scripts to be able to test parts of the architecture individualy. All helpers are in the _helpers_ folder.

## flask_server

A flask server acting as a PlugIt proxy, used by `service_external.py`.

## pop_server

A POP server, used by `service_internal.py` to test the `check_mail` function.

## api_server.py

A flask server acting as a PlugIt service (only the API part) used by `service_internal`.

## doquery_server.py

A flask server implementing differents methods (GET, POST, GET with specials parameters, etc.) used by `service_internal.py` to test the `doQuery` function.
