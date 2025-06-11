from flask import render_template, Blueprint, request, url_for, redirect, session
from app import auth

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/login")
@auth.login_required()
def Login(*, context):
    return redirect(url_for('home.Home'))

@auth_blueprint.route("/logout")
def Logout(*, context):
    session.clear()
    return redirect(url_for('home.Home'))