import sys
import json


from flask import Flask, request
app = Flask(__name__)


@app.route("/test_get")
def test_get():
    return json.dumps({'get_param': request.args.get('get_param', ''), 'method': 'GET'})


@app.route("/test_post", methods=['POST'])
def test_post():
    return json.dumps({'get_param': request.args.get('get_param', ''), 'post_param': request.form.get('post_param', ''), 'method': 'POST'})


@app.route("/test_post_list", methods=['POST'])
def test_post_list():
    return json.dumps({'post_param': request.form.getlist('post_param'), 'method': 'POST'})


@app.route("/test_extraHeaders", methods=['GET', 'POST'])
def test_extraHeaders():
    return json.dumps({'x-plugit-test': request.headers.get('x-plugit-test', '')})


@app.route("/test_session", methods=['GET', 'POST'])
def test_session():
    return json.dumps({'x-plugitsession-test': request.headers.get('x-plugitsession-test', ''), 'cookie-test': request.cookies.get('test', '')})


@app.route("/test_fileupload", methods=['POST'])
def test_fileupload():
    return json.dumps({'file-test': request.files['test'].read()})


if __name__ == "__main__":
    app.run(port=62314)
