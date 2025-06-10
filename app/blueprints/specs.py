from app import auth
from app.models.specs import Spec
from app.helpers import specs_utils as Utils
from flask import render_template, Blueprint, request, redirect, url_for

specs_blueprint = Blueprint("specs", __name__)

@specs_blueprint.route("/zarzadzaj", methods=['POST', 'GET'])
@auth.login_required()
def EditSpecs(*, context):
    """
    Handle specification editing:
    - GET: Display all specifications for editing
    - POST: Process form submissions for adding, editing, or deleting specifications
    """
    allSpecs = Spec.Find()

    if request.method == "POST":

        deleteID = request.form.get("delete")
        if deleteID:
            # Delete a specification
            Spec.DeleteBy_ID(deleteID)
            return redirect(url_for("specs.EditSpecs"))

        # TODO: There's a bug when name of a spec is changed it leaves a blank in the device specs list.
        #       Whenever user changes name it needs to change a name in every device at once.

        if request.form.get("saveAllSpecs"):
            # Process all specification changes from the form
            for spec in request.form:
                # Handle new specifications
                if spec[:7] == "newName":
                    item_id = spec[7:]
                    currentName = request.form.get(spec)
                    optionsList = Utils.ParseToList(request.form.get("newOptions" + item_id))
                    Spec.Create(currentName, optionsList)

                # Handle edited specification names
                if spec[:8] == "editName" and request.form.get(spec):
                    item_id = spec[8:]
                    currentName = request.form.get(spec)
                    Spec.EditName(item_id, currentName)

                # Handle edited specification options
                if spec[:11] == "editOptions":
                    item_id = spec[11:]
                    optionsList = Utils.ParseToList(request.form.get(spec))
                    Spec.EditOptions(item_id, optionsList)


    # Convert options lists to comma-separated strings for display
    alteredSpecs = list(allSpecs)
    for item in alteredSpecs:
        item["options"] = ", ".join(item["options"])

    return render_template("specs/manage.html", specs=alteredSpecs, username=context['user']['name'])