from app import auth, db
from flask import Blueprint, render_template, request, redirect, url_for

from app.models.rooms import Rooms

rooms_blueprint = Blueprint("rooms", __name__)

@rooms_blueprint.route("/zarzadzaj", methods=['POST', 'GET'])
@auth.login_required()
def RoomList(*, context):
    """
    Display and manage rooms:
    - GET: Show paginated list of rooms
    - POST: Update room keepers
    """
    if request.method == "POST":
        # Update room keepers from form
        for room in request.form:
            room_id = room[6:]
            Rooms.Edit(room_id, request.form.get(room))

        return redirect(url_for("rooms.RoomList"))

    # TODO: Optimize pagination

    # Pagination setup
    page = request.args.get('page', 1, type=int)
    per_page = 9
    query = {}
    filter_name = request.args.get('filter', '').strip()
    skip = (page - 1) * per_page

    # Apply name filter if provided
    if filter_name:
        query['name'] = {'$regex': f'.*{filter_name}.*', '$options': 'i'}

    # Get paginated rooms
    allRooms = list(Rooms.Find(query).skip(skip).limit(per_page))

    # Calculate pagination details
    total = db.rooms.count_documents(query)
    total_pages = (total + per_page - 1) // per_page

    return render_template("rooms/manage.html",
                           rooms=allRooms,
                           page=page,
                           total_pages=total_pages,
                           username=context['user']['name'])