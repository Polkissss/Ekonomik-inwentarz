from app import auth
from app.models.rooms import Rooms
from flask import render_template, Blueprint

# Create a Flask Blueprint for the application routes
home_blueprint = Blueprint("home", __name__)

@home_blueprint.route("/")
@auth.login_required()
def Home(*, context):
    """Render the main home page with all rooms"""
    allRooms = Rooms.Find()
    return render_template("home/home.html", rooms=allRooms, username=context['user']['name'])