from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask
from apps.config import app_config_builder, app_blueprint_builder
from apps.config import page_not_found, internal_server_error

def create_app(config_key):
   app = Flask(__name__)

   app = app_config_builder(app, config_key)
   app = app_blueprint_builder(app)
   toolbar = DebugToolbarExtension(app)
   app.register_error_handler(404, page_not_found)
   app.register_error_handler(500, internal_server_error)

   return app