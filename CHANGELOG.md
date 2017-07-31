# v0.3.6

Introduction of `send_etag` decorator, who allow to send an ETag header to the final client, using the `_plugit_etag` value in returned data.
If an *action* return a 304, 401, 403, 404, 429 or 500 status code, the final code will be passed to the final client (before that, only a 200, 404 (for any code not in [200, 500]) or 500 was sent back).


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
