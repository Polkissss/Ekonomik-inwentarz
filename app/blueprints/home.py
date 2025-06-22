from app import auth
from app.helpers.auth_utils import check_first_login
from app.models.rooms import Rooms
from flask import render_template, Blueprint, session, url_for

# Create a Flask Blueprint for the application routes
home_blueprint = Blueprint("home", __name__)

@home_blueprint.route("/")
@auth.login_required()
@check_first_login
def Home(*, context={"user": {"name": "Anonymous", "preffered_username": "Anonymous"}}):
    """Render the main home page with all rooms"""
    allRooms = Rooms.Find()
    return render_template("home/home.html", rooms=allRooms, username=context['user']['name'])