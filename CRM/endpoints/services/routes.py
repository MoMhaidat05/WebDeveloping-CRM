from flask import Blueprint, render_template
from CRM import db
from CRM.models import Service


services_bp = Blueprint("services", __name__)


@services_bp.route("/services", methods=["GET"])
def services():
    all_services = (
        db.session.query(Service).order_by(Service.start_date.desc()).all()
    )
    return render_template(
        "services.html", services=all_services, title="Services - CRM System"
    )
