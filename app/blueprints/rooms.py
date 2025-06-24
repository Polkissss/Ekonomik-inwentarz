from app import auth
from flask import Blueprint, render_template, request, redirect, url_for

from app.models.rooms import Rooms
from app.models.users import Users
from app.helpers.auth_utils import check_first_login

rooms_blueprint = Blueprint("rooms", __name__)

@rooms_blueprint.route("/zarzadzaj", methods=['POST', 'GET'])
@auth.login_required()
@check_first_login
def RoomList(*, context={"user": {"name": "Anonymous", "preffered_username": "Anonymous"}}):
    """
    Display and manage rooms:
    - GET: Show paginated list of rooms
    - POST: Update room keepers
    """
    if request.method == "POST":
        # Update room keepers from form
        for room in request.form:
            room_id = room[6:]
            editedRoom = Rooms.Edit(room_id, request.form.get(room))

        return redirect(url_for("rooms.RoomList"))


    # Pagination setup
    page = request.args.get('page', 1, type=int)
    perPage = 9
    query = {}
    filterName = request.args.get('filter', '').strip()
    skip = (page - 1) * perPage

    # Apply name filter if provided
    if filterName:
        query['name'] = {'$regex': f'.*{filterName}.*', '$options': 'i'}

    # Get paginated rooms
    allRooms = list(Rooms.Find(query).skip(skip).limit(perPage))

    # Calculate pagination details
    total = Rooms.TotalDocuments(query)
    totalPages = (total + perPage - 1) // perPage

    return render_template("rooms/manage.html",
                           rooms=allRooms,
                           page=page,
                           total_pages=totalPages,
                           username=context['user']['name'])