HowTo
=====

The point of this document is to explain how to create a basic PlugIt project, with submodules, a database and deployements scripts.

# Basic setup

## Copy files from base project

First, copy files from `Simple Flask server` folder. This ensure you have latest version of different files. Remove everything in `actions.py` and all files in `media/` and `templates` folder.

## Create a config.py

To store configuration for the project, create a `config.py` file and a `config.py.dist` file. Ignore the `config.py` file in your favorite [SCM](https://en.wikipedia.org/wiki/Source_code_management), to avoid the publication of private settings.

Add the following settings in your `config.py` and `config.py.dist`:

    API_URL = ""
    SQLALCHEMY_URL = ""
    DEBUG = True
    PI_BASE_URL = '/'
    PI_ALLOWED_NETWORKS = ['127.0.0.1/32']

Set `API_URL` to your PlugIT client API. If you're using the _Simple Django client_ you can use `http://127.0.0.1:8000/plugIt/ebuio_api/`.

## Submodules

If your project has multiple parts, it's better to have differents modules for code organization. If your application is simple, just implement your actions in `actions.py`. Otherwhise, create differents folders/python modules (e.g.: `mkdir users && touch users/__init__.py`) and just import them into `actions.py` (e.g.: `from users.actions import *`). You can then create an `actions.py` file in each directory and implement your actions as usual.

# Database

The database will be handeled by [SQLAlchemy](http://www.sqlalchemy.org/). You can read the documentation for details on the website.

We're going to use [Alembic](https://pypi.python.org/pypi/alembic) to manage differents versions of the database. Each time you modify the model, a file with be generated with commands to upgrade the database, allowing easy update of them for everyone working on your projects (including the production server ;)).

You need to setup your database: decide the type of the database (mysql, sqlite, etc.), create it and if needed, create a user. Then setup the `SQLALCHEMY_URL` option in your `config.py` file with all informations needed. Example: `mysql://myuser:mypassword@localhost/mydatabase` or `sqlite:///database.sq3`.

Then, edit the `utils.py` file to create the `get_db` function who is going to return the SQLAlchemy object to access the database:

    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy
    import config
    def get_db():
        """Return the database"""

        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_URL
        db = SQLAlchemy(app)

        return db

## models.py

Create a `models.py` file. You will implement your models here. At the begining of the file, import database-related objects:

    from utils import get_db
    db = get_db()

And create your models after. Example:

    class Table(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(80))

### json property

As data returned by PlugIt actions have to be json, it's usefull to add a property to convert your entires directly to json. Add this function at the beggining your `models.py` file:

    def to_json(inst, cls, bonusProps=[]):
        """
        Jsonify the sql alchemy query result.
        """
        convert = dict()
        # add your coversions for things like datetime's
        # and what-not that aren't serializable.
        d = dict()
        for c in cls.__table__.columns:
            v = getattr(inst, c.name)
            if c.type in convert.keys() and v is not None:
                try:
                    d[c.name] = convert[c.type](v)
                except:
                    d[c.name] = "Error:  Failed to covert using ", str(convert[c.type])
            elif v is None:
                d[c.name] = str()
            else:
                d[c.name] = v
        for p in bonusProps:
            d[p] = getattr(inst, p)

        return d

and add the property to your models:

    class Table(db.Model):
        (...)
        @property
        def json(self):
            return to_json(self, self.__class__, [])

All model's fields will be used. If you want to add more information (e.g. custom properties), you can add them to the list (3th parameter) of the `to_json` function.

## Alembic 

### Setup

Run `alembic init alembic` inside your project directory. It's will create basic configration files in the _alembic_ folder.

Then we need to edit configuration to use your config.py instead of the alembic.ini file.

At line 12, after `fileConfig(config.config_file_name)`, add:

    import sys

    # To acces models, add the current path
    sys.path.append('.')

At line 23, replace `target_metadata = None` by

    from models import db
    target_metadata = db.metadata

At line 42, replace `url = config.get_main_option("sqlalchemy.url")` with

    import config as app_config
    url = app_config.SQLALCHEMY_URL

And at line 56, remplace `engine = engine_from_config(
    config.get_section(config.config_ini_section),` by 

    alembic_config = config.get_section(config.config_ini_section)
    import config as app_config
    alembic_config['sqlalchemy.url'] = app_config.SQLALCHEMY_URL

    engine = engine_from_config(
        alembic_config,

### Commands

When alembic is setup you can:

* Create a new revision:
`alembic revision --autogenerate -m 'message'`

* Upgrade the database to the latest version:
`alembic upgrade head`

## Do queries !

You should now be able to use your models to store informations in the database. Check the documentation for detailed usage of sqlalchemy, but importants queries are:

* Filter and order all entries of a table: `Table.query.filter(Table.status == 'published').order_by(Table.name).all()`
* Get one entry of a table: `Table.query.filter(Table.id == request.args['id']).first()`
* Create a new record: `t = Table(); t.name = 'The game'; db.session.add(t); db.session.commit()`
* Delete a record: `db.session.delete(t); db.session.commit()`

Assumming you imported the Table model and created the db object like this: `from models import db, Table`

# Deployement script

You can use deployement script of others projects as a base, e.g. [ebuio-qc](https://github.com/ebu/ebuio-qc/tree/develop/Deployement).

You will need to:

* Setup the database
* Setup apache
* Get code from your SCM
* Run `alembic upgrade head`

To run the flask server with apache, a wsgi is used. As an example, here is a basic `wsgi.py`:

    import os
    os.chdir('/folder/to/your/project')

    from server import app as application

Example: apache configuration you may use:

    <VirtualHost *:80>
        ServerName <YourProject>.ebu.io

        ErrorLog "/home/ubuntu/logs/error.log"
        LogFormat "%h %l %u %t \"%r\" %>s %b" common
        CustomLog "/home/ubuntu/logs/access.log" common

        WSGIDaemonProcess flask processes=1 threads=1 display-name=%{GROUP} python-path=/folder/to/your/project/
        WSGIProcessGroup flask
        WSGIScriptAlias / /folder/to/your/project/wsgi.py
        WSGIApplicationGroup %{GLOBAL}
        WSGIPassAuthorization On

        <Directory /folder/to/your/project/>
            Order Allow,Deny
            Allow from All
            Require all granted
        </Directory>

    </VirtualHost>

In the `config.py` file you use on your server, don't forget to set `DEBUG  = False`.