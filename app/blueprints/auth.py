from flask import Blueprint, url_for, redirect, session
from app.models.settings import Settings
from app.models.users import Users
from datetime import datetime
from app import auth

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/login", methods=["GET", "POST"])
@auth.login_required()
def Login(*, context):

    if Settings.GetFilterState():
        print("filtr dziala!")

    if not Users.FindOne({"name": context["user"]["preferred_username"]}):
        Users.Create(context["user"]["preferred_username"], False, datetime.now())
    else:
        Users.EditLastLogin(context["user"]["preferred_username"])

    return redirect(url_for("home.Home"))

@auth_blueprint.route("/logout", methods=["GET", "POST"])
def Logout():
    session.clear()
    auth.logout()
    return redirect(url_for('home.Home'))