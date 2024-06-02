import os, flask,json
from flask import Flask, request, redirect, url_for, render_template

def create_app(test_config=None):
    """ Application factory function """
    # create and configure the app
    app = Flask(__name__)

    basedir = os.path.join(app.instance_path, "..")
    # make sure the instance folder exists
    from .routes import main
    app.register_blueprint(main)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app