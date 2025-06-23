from flask import render_template, Blueprint, request, redirect, url_for, flash
from werkzeug.routing import ValidationError
from app.models.users import Users
from app.models.settings import Settings
from app.helpers.auth_utils import check_first_login
from app import auth

users_blueprint = Blueprint("users", __name__)

@users_blueprint.route("/zarzadzaj", methods=['POST', 'GET'])
@auth.login_required()
@check_first_login
def ManageUsers(*, context={"user": {"name": "Anonymous", "preferred_username": "Anonymous"}}):
    allUsers = list(Users.Find())
    currentFilter = Settings.GetFilterState()

    if context['user']['name'] != "Anonymous":
        currentUserInfo = Users.FindOne({"name": context['user']['preferred_username']})
        currentUserPriviledge = currentUserInfo["permission"]
    else:
        currentUserPriviledge = False

    if request.method == "POST":

        if request.form.get("toggleFilterState"):
            Settings.UpdateFilter(not currentFilter)
            return redirect(url_for("users.ManageUsers"))

        if request.form.get("addUser"):
            newName = request.form.get("newName") + "@ekonomik.gniezno.pl"
            newPermission = request.form.get("newPermission")

            try:
                Users.Create(newName, newPermission, "brak")
            except ValidationError as e:
                flash(str(e), "danger")
                return redirect(url_for("users.ManageUsers"))

            return redirect(url_for("users.ManageUsers"))

        if request.form.get("updateSingleUser"):
            user_id = request.form.get("updateSingleUser")
            editPriviledge = request.form.get(f"permission{user_id}")

            if editPriviledge:
                editPriviledge = True
            else:
                editPriviledge = False

            userToEdit = Users.FindBy_ID(user_id)

            try:
                Users.EditPrviledges(userToEdit["name"], editPriviledge)
            except:
                print("error")

            return redirect(url_for("users.ManageUsers"))

        if request.form.get("deleteUser"):
            try:
                Users.DeleteBy_ID(request.form.get("deleteUser"))
            except:
                print("error")

            return redirect(url_for("users.ManageUsers"))


    return render_template("users/manage.html", users=allUsers, username=context['user']['name'], currentUser=context['user']['preferred_username'], filterState=currentFilter, currentPriviledge=currentUserPriviledge)