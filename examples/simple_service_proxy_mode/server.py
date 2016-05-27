#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Run as a simple flask application

from flask import Flask, request, render_template, make_response
app = Flask(__name__)


def get_ebuio_headers(request):
    """Return a dict with ebuio headers"""

    retour = {}

    for (key, value) in request.headers:
        if key.startswith('X-Plugit-'):
            key = key[9:]

            retour[key] = value

    return retour


def base_demo(request, mode):
    headers = get_ebuio_headers(request)

    base_url = headers['Base-Url']

    return render_template('demo.html', mode=mode, headers=headers, base_url=base_url)


@app.route("/")
def demo():
    return base_demo(request, 'GET')


@app.route("/post", methods=['POST'])
def post():
    return base_demo(request, 'POST')


@app.route("/no_template")
def no_template():

    response = make_response("This is not inside a template")
    response.headers['EbuIo-PlugIt-NoTemplate'] = 'Yes'
    return response


@app.route("/redirect_me")
def redirect_me():

    response = make_response("")
    response.headers['EbuIo-PlugIt-Redirect'] = '/'
    return response


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
