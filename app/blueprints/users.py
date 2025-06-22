from flask import render_template, Blueprint, request, redirect, url_for, flash
from app.models.users import Users
from app.models.settings import Settings
from app.helpers.auth_utils import check_first_login
from app import auth

users_blueprint = Blueprint("users", __name__)

@users_blueprint.route("/zarzadzaj", methods=['POST', 'GET'])
@auth.login_required()
@check_first_login
def ManageUsers(*, context={"user": {"name": "Anonymous", "preffered_username": "Anonymous"}}):
    return render_template("users/manage.html")