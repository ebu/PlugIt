import sys
import json


if len(sys.argv) != 7:
    print "Wrong number of arguemnts"
    sys.exit(1)

user_key = sys.argv[1]
orgas_key = sys.argv[2]
orga_key = sys.argv[3]
project_members_key = sys.argv[4]
send_mail_key = sys.argv[5]
forum_key = sys.argv[6]


from flask import Flask, request
app = Flask(__name__)


@app.route("/user/<pk>")
def test_user(pk):

    if pk == user_key[3]:
        return json.dumps({user_key[::-1]: user_key})


@app.route("/orgas/")
def test_orgas():
    retour = []

    for x in orgas_key:
        retour.append({'id': x, orgas_key.replace(x, '')[::-1]: orgas_key.replace(x, '')})

    return json.dumps({'data': retour})


@app.route("/orga/<pk>")
def test_orga(pk):

    if pk == orga_key[3]:
        return json.dumps({orga_key[::-1]: orga_key})


@app.route("/members/")
def test_members():
    retour = []

    for x in project_members_key:
        retour.append({'id': x, project_members_key.replace(x, '')[::-1]: project_members_key.replace(x, '')})

    return json.dumps({'members': retour})


@app.route("/mail/", methods=['POST'])
def test_mail():

    if request.form.get('sender') != send_mail_key[1]:
        return ""
    if request.form.get('subject') != send_mail_key[5]:
        return ""
    if send_mail_key[0] not in request.form.getlist('dests'):
        return ""
    if send_mail_key[4] not in request.form.getlist('dests'):
        return ""
    if request.form.get('message') != send_mail_key[9]:
        return ""
    if request.form.get('response_id') == send_mail_key[7]:
        return send_mail_key[::-1]

    return send_mail_key


@app.route("/ebuio/forum/", methods=['POST'])
def test_send_forum():

    if request.form.get('subject') != forum_key[2]:
        return "{}"
    if request.form.get('author') != forum_key[6]:
        return "{}"
    if request.form.get('message') != forum_key[10]:
        return "{}"
    if request.form.get('tags') == forum_key[8]:
        return json.dumps({'key': forum_key[::-1]})

    return json.dumps({'key': forum_key})

if __name__ == "__main__":
    app.run(port=62312)
