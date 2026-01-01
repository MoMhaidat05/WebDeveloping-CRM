from flask import Blueprint, render_template
from CRM import db
from CRM.models import Client, Service, Financial, ActivityLog
from datetime import datetime
from sqlalchemy import extract
import calendar

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET", "POST"])
def index():
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_month_name = calendar.month_abbr[current_month]
    clients_this_month = len(
        db.session.query(Client)
        .filter(extract("month", Client.created_at) == current_month)
        .all()
    )
    services_this_month = len(
        db.session.query(Service)
        .filter(extract("month", Service.start_date) == current_month)
        .all()
    )
    total_earnings_this_month = (
        db.session.query(Financial)
        .filter(extract("month", Financial.created_at) == current_month)
        .all()
    )
    sum_of_earnings = sum(
        bill.paid_amount for bill in total_earnings_this_month
    )

    last_activities = (
        db.session.query(ActivityLog)
        .order_by(ActivityLog.timestamp.desc())
        .limit(5)
        .all()
    )
    return render_template(
        "index.html",
        title="Home - CRM System",
        clients=clients_this_month,
        services=services_this_month,
        month=current_month_name,
        sum_of_earnings=sum_of_earnings,
        year=current_year,
        last_activities=last_activities,
    )
