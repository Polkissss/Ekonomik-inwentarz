from flask import Flask, redirect, url_for
from flask_pymongo import PyMongo
from app.helpers.auth_utils import ModifiedAuth

from .config import *

# Initialize Flask app
app = Flask(__name__)

# Load configuration from the app_config file
app.config["SESSION_TYPE"] = settings.SESSION_TYPE
app.config["SECRET_KEY"] = settings.SECRET_KEY
app.config["MONGO_URI"] = mongo_settings.MONGO_URI

# Set up the authentication
auth = ModifiedAuth(
    app,
    authority=azure_settings.AUTHORITY,
    client_id=azure_settings.CLIENT_ID,
    client_credential=azure_settings.CLIENT_SECRET,
    redirect_uri=azure_settings.REDIRECT_URI,
    login_toggle=settings.LOGIN_ENABLED
)

# Initialize MongoDB
mDB = PyMongo(ssl=True, ssl_cert_reqs='CERT_NONE')
mDB.init_app(app)
db = mDB.db

# Register blueprints for app views
from .blueprints import *
app.register_blueprint(home.home_blueprint, url_prefix='/strona-glowna')
app.register_blueprint(device.device_blueprint, url_prefix='/urzadzenie')
app.register_blueprint(specs.specs_blueprint, url_prefix='/specyfikacje')
app.register_blueprint(rooms.rooms_blueprint, url_prefix='/pomieszczenia')
app.register_blueprint(auth.auth_blueprint, url_prefix='/autoryzacja')
app.register_blueprint(users.users_blueprint, url_prefix='/uzytkownicy')

# Initialize settings in database especially important during first run
from app.models.settings import Settings
# if not Settings.Find({"name": "user_filtration"}):
Settings.UpdateFilter(False)

# Reditect users to the main page on empty route
@app.route("/")
def DefaultRedirect():
    return redirect(url_for("home.Home"))