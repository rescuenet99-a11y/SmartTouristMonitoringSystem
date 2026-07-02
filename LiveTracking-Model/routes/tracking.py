from flask import Blueprint
from flask import render_template

tracking_bp = Blueprint(
    "tracking",
    __name__
)

@tracking_bp.route("/tracking")
def tracking():

    return render_template(
        "tracking.html"
    )