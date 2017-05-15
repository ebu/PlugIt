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