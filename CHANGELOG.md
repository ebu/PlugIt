# v0.3.11

* New API call: `/user/<pk>/techgroups/` return the list of the techgroups of the user (EBUIo only)
* New API call: `/techgroups/` return the list of the techgroups (EBUIo only)

# v0.3.9

* Fixed a bug in 'api.send_mail' where 'html_message' was always considered true.

# v0.3.8

Make "Cross-origin resource sharing" working:
* Introduction of `crossdomain` decorator, who will automaticaly reply CORS headers (inclution OPTIONS requests)
* Client CORS headers are forwarded to PlugIt services (`X-PlugIt-Origin`, `X-PlugIt-Access-Control-Request-Method` and `X-PlugIt-Access-Control-Request-Headers`
* Services' CROS headers are forwarded back to clients (`Access-Control-Allow-Origin`, `Access-Control-Allow-Credentials`, `Access-Control-Expose-Headers`, `Access-Control-Max-Age`, `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`)
* OPTIONS method is forwarded to services.
* It's services reposibility to handle and if needed refuse to reply to some requests based on `Origin` header. The PlugIt proxy only act as a proxy.


# v0.3.7

Allow POPS to be used.

# v0.3.6

Introduction of `send_etag` decorator, who allow to send an ETag header to the final client, using the `_plugit_etag` value in returned data.
The `If-None-Match` http header is forwarded to the service, as `X-PlugIt-If-None_match`.
If an *action* return a 304, 401, 403, 404, 429 or 500 status code, the final code will be passed to the final client (before that, only a 200, 404 (for any code not in [200, 500]) or 500 was sent back).
The caching of the include tag has been improved.
The Cache-Control header of media requests is forwarded to the client.


# v0.3.5

Introduction of `X-Plugit-Remote-Addr` header, with the source IP of the user doing the request on the proxy side.

# v0.3.4

Introduction of the `PI_USE_PROXY_IP` setting, allowing PlugIt services to do remote ip check behind a proxy.

# v0.3.3

Fix django methods used to resolve the hostname to take into account possible usage behind revers proxy server.

# v0.3.1

Small fix for proxy, when not used in standalone mode

# v0.3.0

Major update with new architecture of the project.

* `Dockerfile` to run examples
* Renamming of `client` to `proxy` and `server` to `service`
* PlugIt proxy and service usable as a library, instead of copying the code localy to a project
* New tests
* Multiples bug fixes
* Updated examples

As a service, you can now remove your local plugit folder and use the `plugit` library instead (`pip install plugit`).
If you had a `mail` function in `plugit/routes.py`, you can move it to your local `actions.py` file and pass the function to the `load_actions`.
Everything else should be compatible with previous versions.
