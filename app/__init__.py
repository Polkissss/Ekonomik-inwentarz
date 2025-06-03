from flask import Flask
from flask_pymongo import PyMongo
from identity.flask import Auth
import app.app_config as app_config

# Initialize Flask app
app = Flask(__name__)

# Load configuration from the app_config file
app.config.from_object(app_config)

# Set up the authentication
LOGIN_TOGGLE = app.config["LOGIN_ENABLED"]
if LOGIN_TOGGLE:
    auth = Auth(
        app,
        authority=app.config["AUTHORITY"],
        client_id=app.config["CLIENT_ID"],
        client_credential=app.config["CLIENT_SECRET"],
        redirect_uri=app.config["REDIRECT_URI"]
    )

# Initialize MongoDB
mDB = PyMongo()
mDB.init_app(app)
db = mDB.db

# Register blueprints for app views
from app.views import app_blueprint
app.register_blueprint(app_blueprint)

# Additional views if needed
from app import views