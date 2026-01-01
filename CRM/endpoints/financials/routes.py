from flask import Blueprint, render_template
from CRM import db
from CRM.models import Financial


financials_bp = Blueprint("financials", __name__)


@financials_bp.route("/financials", methods=["GET"])
def financials():
    all_financials = (
        db.session.query(Financial).order_by(Financial.created_at.desc()).all()
    )
    return render_template(
        "financials.html",
        financials=all_financials,
        title="Financials - CRM System",
    )
