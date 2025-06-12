from flask import Flask, redirect, url_for
from flask_pymongo import PyMongo
from identity.flask import Auth

from .config import *

# Initialize Flask app
app = Flask(__name__)

# Load configuration from the app_config file
app.config["SESSION_TYPE"] = settings.SESSION_TYPE
app.config["SECRET_KEY"] = settings.SECRET_KEY
app.config["MONGO_URI"] = mongo_settings.MONGO_URI

# TODO: Setup a wraper to make login toggleable

# Set up the authentication
auth = Auth(
    app,
    authority=azure_settings.AUTHORITY,
    client_id=azure_settings.CLIENT_ID,
    client_credential=azure_settings.CLIENT_SECRET,
    redirect_uri=azure_settings.REDIRECT_URI
)

# Initialize MongoDB
mDB = PyMongo()
mDB.init_app(app)
db = mDB.db

# Register blueprints for app views
from .blueprints import *
app.register_blueprint(home.home_blueprint, url_prefix='/strona-glowna')
app.register_blueprint(device.device_blueprint, url_prefix='/urzadzenie')
app.register_blueprint(specs.specs_blueprint, url_prefix='/specyfikacje')
app.register_blueprint(rooms.rooms_blueprint, url_prefix='/pomieszczenia')
app.register_blueprint(auth.auth_blueprint, url_prefix='/autoryzacja')

@app.route("/")
def DefaultRedirect():
    return redirect(url_for("home.Home"))