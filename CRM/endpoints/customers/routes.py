from flask import Blueprint, render_template
from CRM import db
from CRM.models import Client


customers_bp = Blueprint("clients", __name__)


@customers_bp.route("/clients", methods=["GET"])
def clients():
    all_clients = (
        db.session.query(Client).order_by(Client.created_at.desc()).all()
    )
    return render_template(
        "clients.html", clients=all_clients, title="Customers - CRM System"
    )
