from flask import Blueprint, request, jsonify
from CRM import db
from CRM.models import (
    Client,
    Service,
    Financial,
    ActivityLog,
)
from datetime import datetime
from sqlalchemy import extract
import calendar

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/get_recap", methods=["POST"])
def stats():
    try:
        json_data = request.get_json()
    except Exception as e:
        return jsonify({"error": "Invalid JSON data"}), 400
    try:
        month_abbr = json_data.get("month", datetime.now().month)
        current_month = list(calendar.month_abbr).index(month_abbr)
        current_year = int(json_data.get("year", datetime.now().year))
        current_month_abbr = calendar.month_abbr[current_month]
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
        return (
            jsonify(
                {
                    "clients": clients_this_month,
                    "services": services_this_month,
                    "month": current_month_abbr,
                    "sum_of_earnings": sum_of_earnings,
                    "year": current_year,
                }
            ),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


@api_bp.route("/api/clients", methods=["GET", "POST", "DELETE", "PUT"])
def clients():
    if request.method == "GET":
        all_clients = (
            db.session.query(Client).order_by(Client.created_at.desc()).all()
        )
        clients_list = []
        for client in all_clients:
            clients_list.append(
                {
                    "id": client.id,
                    "full_name": client.full_name,
                    "nickname": client.nickname,
                    "phone_primary": client.phone_primary,
                    "phone_secondary": client.phone_secondary,
                    "email": client.email,
                    "business_name": client.business_name,
                    "city": client.city,
                    "location_url": client.location_url,
                    "status": client.status,
                    "created_at": client.created_at.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )
        return jsonify({"clients": clients_list}), 200
    if request.method == "POST":
        try:
            json_data = request.get_json()
        except Exception as e:
            return jsonify({"error": "Invalid JSON data"}), 400
        try:
            new_client = Client(
                full_name=json_data.get("full_name", "Unnamed Client"),
                nickname=json_data.get("nickname", "No Nickname"),
                phone_primary=json_data.get("phone_primary", "NULL"),
                phone_secondary=json_data.get("phone_secondary", None),
                email=json_data.get("email", None),
                business_name=json_data.get("business_name", None),
                city=json_data.get("city", "No City Provided"),
                location_url=json_data.get("location_url", None),
                status=json_data.get("status", "Active"),
                created_at=datetime.now(),
            )
            db.session.add(new_client)
            db.session.commit()
            activity_log = ActivityLog(
                client_id=new_client.id,
                action_type="Client Created",
                description=f"Client {new_client.full_name} created.",
                timestamp=datetime.now(),
            )
            db.session.add(activity_log)
            db.session.commit()
            return (
                jsonify(
                    {
                        "message": "Client added successfully",
                        "client": {
                            "full_name": new_client.full_name,
                            "nickname": new_client.nickname,
                            "phone_primary": new_client.phone_primary,
                            "phone_secondary": new_client.phone_secondary,
                            "email": new_client.email,
                            "business_name": new_client.business_name,
                            "city": new_client.city,
                            "location_url": new_client.location_url,
                            "status": new_client.status,
                            "id": new_client.id,
                        },
                    }
                ),
                201,
            )
        
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    elif request.method == "DELETE":
        try:
            client_id = request.args.get("id")
            client = db.session.query(Client).get(client_id)
            if not client:
                return jsonify({"error": "Client not found"}), 404
            db.session.delete(client)
            db.session.commit()
            return jsonify({"message": "Client deleted successfully"}), 200
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    elif request.method == "PUT":
        try:
            json_data = request.get_json()
        except Exception as e:
            return jsonify({"error": "Invalid JSON data"}), 400
        try:
            client_id = json_data.get("client_id")
            client = db.session.query(Client).get(client_id)
            if not client:
                return jsonify({"error": "Client not found"}), 404
            client.full_name = json_data.get("full_name", client.full_name)
            client.nickname = json_data.get("nickname", client.nickname)
            client.phone_primary = json_data.get(
                "phone_primary", client.phone_primary
            )
            client.phone_secondary = json_data.get(
                "phone_secondary", client.phone_secondary
            )
            client.email = json_data.get("email", client.email)
            client.business_name = json_data.get(
                "business_name", client.business_name
            )
            client.city = json_data.get("city", client.city)
            client.location_url = json_data.get(
                "location_url", client.location_url
            )
            client.status = json_data.get("status", client.status)
            db.session.commit()
            activity_log = ActivityLog(
                client_id=client.id,
                action_type="Client Updated",
                description=f"Client {client.full_name} updated.",
                timestamp=datetime.now(),
            )
            db.session.add(activity_log)
            db.session.commit()
            return jsonify({"message": "Client updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500

@api_bp.route("/api/services", methods=["GET", "POST", "DELETE", "PUT"])
def services():
    if request.method == "GET":
        all_services = (
            db.session.query(Service).order_by(Service.start_date.desc()).all()
        )
        services_list = []
        for service in all_services:
            services_list.append(
                {
                    "id": service.id,
                    "client_id": service.client_id,
                    "domain_name": service.domain_name,
                    "domain_registrar": service.domain_registrar,
                    "domain_expiry_date": service.domain_expiry_date.strftime("%Y-%m-%d") if service.domain_expiry_date else None,
                    "hosting_provider": service.hosting_provider,
                    "server_ip": service.server_ip,
                    "ssh_port": service.ssh_port,
                    "hosting_expiry_date": service.hosting_expiry_date.strftime("%Y-%m-%d") if service.hosting_expiry_date else None,
                    "tech_stack": service.tech_stack,
                    "description": service.description,
                    "start_date": service.start_date.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": service.end_date.strftime("%Y-%m-%d %H:%M:%S") if service.end_date else None,
                }
            )
        return jsonify({"services": services_list}), 200
    elif request.method == "POST":
        json_data = request.get_json()
        new_service = Service(
            client_id=json_data.get("client_id"),
            domain_name=json_data.get("domain_name"),
            domain_registrar=json_data.get("domain_registrar", "NameCheap"),
            domain_expiry_date=json_data.get("domain_expiry_date") if json_data.get("domain_expiry_date") else None,
            hosting_provider=json_data.get("hosting_provider") if json_data.get("hosting_provider") else None,
            server_ip=json_data.get("server_ip") if json_data.get("server_ip") else None,
            ssh_port=json_data.get("ssh_port") if json_data.get("ssh_port") else 22,
            hosting_expiry_date=json_data.get("hosting_expiry_date") if json_data.get("hosting_expiry_date") else None,
            tech_stack=json_data.get("tech_stack") if json_data.get("tech_stack") else None,
            description=json_data.get("description") if json_data.get("description") else None,
            start_date=json_data.get("start_date", datetime.now()),
            end_date=json_data.get("end_date") if json_data.get("end_date") else None,
        )
        db.session.add(new_service)
        db.session.commit()
        client = db.session.query(Client).get(new_service.client_id)
        activity_log = ActivityLog(
            client_id=new_service.client_id,
            action_type="Service Created",
            description=f"Service {new_service.domain_name} created for client {client.full_name}.",
            timestamp=datetime.now(),
        )
        db.session.add(activity_log)
        db.session.commit()
        return jsonify({"message": "Service created successfully"}), 201
    elif request.method == "DELETE":
        service_id = request.args.get("id")
        service = db.session.query(Service).get(service_id)
        if not service:
            return jsonify({"error": "Service not found"}), 404
        db.session.delete(service)
        db.session.commit()
        return jsonify({"message": "Service deleted successfully"}), 200
    elif request.method == "PUT":
        try:
            json_data = request.get_json()
            service_id = json_data.get("id")
            service = db.session.query(Service).get(service_id)
            if not service:
                return jsonify({"error": "Service not found"}), 404
            service.client_id = json_data.get("client_id", service.client_id)
            service.domain_name = json_data.get("domain_name", service.domain_name)
            service.domain_registrar = json_data.get("domain_registrar", service.domain_registrar)
            service.domain_expiry_date = json_data.get("domain_expiry_date", service.domain_expiry_date)
            service.hosting_provider = json_data.get("hosting_provider", service.hosting_provider)
            service.server_ip = json_data.get("server_ip", service.server_ip)
            service.ssh_port = json_data.get("ssh_port", service.ssh_port)
            service.hosting_expiry_date = json_data.get("hosting_expiry_date", service.hosting_expiry_date)
            service.tech_stack = json_data.get("tech_stack", service.tech_stack)
            service.description = json_data.get("description", service.description)
            db.session.commit()
            activity_log = ActivityLog(
                client_id=service.client_id,
                action_type="Service Updated",
                description=f"Service {service.domain_name} updated.",
                timestamp=datetime.now(),
            )
            db.session.add(activity_log)
            db.session.commit()
            return jsonify({"message": "Service updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500
    return jsonify({"message": "Method not implemented"}), 501

@api_bp.route("/api/financials", methods=["GET", "POST", "DELETE", "PUT"])
def financials():
    if request.method == "GET":
        all_financials = (
            db.session.query(Financial).order_by(Financial.created_at.desc()).all()
        )
        financials_list = []
        for item in all_financials:
            # Need to fetch client name to display in frontend
            # We can either join query or fetch here. Accessing item.client relies on backref.
            financials_list.append(
                {
                    "id": item.id,
                    "client_id": item.client_id,
                    "client": {
                        "full_name": item.client.full_name if item.client else "Unknown"
                    },
                    "project_title": item.project_title,
                    "total_amount": item.total_amount,
                    "paid_amount": item.paid_amount,
                    "renewal_price": item.renewal_price,
                    "next_renewal_date": item.next_renewal_date.strftime("%Y-%m-%d") if item.next_renewal_date else None,
                    "last_payment_date": item.last_payment_date.strftime("%Y-%m-%d") if item.last_payment_date else None,
                    "remaining_amount": item.remaining_amount, # This is a property, so it's calculated
                    "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        return jsonify(financials_list), 200

    elif request.method == "POST":
        try:
            json_data = request.get_json()
            
            # Helper to convert empty strings to None for dates
            def parse_date(date_str):
                if not date_str or date_str == "":
                    return None
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    return None

            new_financial = Financial(
                client_id=json_data.get("client_id"),
                project_title=json_data.get("project_title"),
                total_amount=float(json_data.get("total_amount") or 0.0),
                paid_amount=float(json_data.get("paid_amount") or 0.0),
                renewal_price=float(json_data.get("renewal_price") or 0.0),
                next_renewal_date=parse_date(json_data.get("next_renewal_date")),
                last_payment_date=parse_date(json_data.get("last_payment_date")),
                created_at=datetime.now()
            )
            
            db.session.add(new_financial)
            db.session.commit()
            
            # Log activity
            client = db.session.query(Client).get(new_financial.client_id)
            activity_log = ActivityLog(
                client_id=new_financial.client_id,
                action_type="Financial Record Created",
                description=f"Financial record '{new_financial.project_title}' created for {client.full_name}.",
                timestamp=datetime.now(),
            )
            db.session.add(activity_log)
            db.session.commit()

            # Return the created object structure so frontend can update immediately
            created_data = {
                "id": new_financial.id,
                "client_id": new_financial.client_id,
                "client": {"full_name": client.full_name},
                "project_title": new_financial.project_title,
                "total_amount": new_financial.total_amount,
                "paid_amount": new_financial.paid_amount,
                "renewal_price": new_financial.renewal_price,
                "next_renewal_date": new_financial.next_renewal_date.strftime("%Y-%m-%d") if new_financial.next_renewal_date else None,
                "last_payment_date": new_financial.last_payment_date.strftime("%Y-%m-%d") if new_financial.last_payment_date else None,
                "remaining_amount": new_financial.remaining_amount
            }
            
            return jsonify({"message": "Financial record added successfully", "financial": created_data}), 201
            
        except Exception as e:
            print(e)
            return jsonify({"error": "Internal server error"}), 500

    elif request.method == "PUT":
        try:
            json_data = request.get_json()
            financial_id = json_data.get("id")
            financial = db.session.query(Financial).get(financial_id)
            
            if not financial:
                return jsonify({"error": "Financial record not found"}), 404

            # Helper to convert empty strings to None for dates
            def parse_date(date_str):
                if not date_str or date_str == "":
                    return None
                try:
                    # Handle both full datetime string or just date string
                    if " " in date_str:
                         return datetime.strptime(date_str.split(" ")[0], "%Y-%m-%d").date()
                    return datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    return None

            # Update fields
            if "client_id" in json_data:
                financial.client_id = json_data.get("client_id")
            if "project_title" in json_data:
                financial.project_title = json_data.get("project_title")
            if "total_amount" in json_data:
                financial.total_amount = float(json_data.get("total_amount") or 0.0)
            if "paid_amount" in json_data:
                financial.paid_amount = float(json_data.get("paid_amount") or 0.0)
            if "renewal_price" in json_data:
                financial.renewal_price = float(json_data.get("renewal_price") or 0.0)
            if "next_renewal_date" in json_data:
                financial.next_renewal_date = parse_date(json_data.get("next_renewal_date"))
            if "last_payment_date" in json_data:
                financial.last_payment_date = parse_date(json_data.get("last_payment_date"))

            db.session.commit()

            # Log activity
            activity_log = ActivityLog(
                client_id=financial.client_id,
                action_type="Financial Record Updated",
                description=f"Financial record '{financial.project_title}' updated.",
                timestamp=datetime.now(),
            )
            db.session.add(activity_log)
            db.session.commit()

            # Return updated object
            updated_data = {
                "id": financial.id,
                "client_id": financial.client_id,
                "client": {"full_name": financial.client.full_name},
                "project_title": financial.project_title,
                "total_amount": financial.total_amount,
                "paid_amount": financial.paid_amount,
                "renewal_price": financial.renewal_price,
                "next_renewal_date": financial.next_renewal_date.strftime("%Y-%m-%d") if financial.next_renewal_date else None,
                "last_payment_date": financial.last_payment_date.strftime("%Y-%m-%d") if financial.last_payment_date else None,
                "remaining_amount": financial.remaining_amount
            }

            return jsonify({"message": "Financial record updated successfully", "financial": updated_data}), 200
            
        except Exception as e:
            print(e)
            return jsonify({"error": "Internal server error"}), 500

    elif request.method == "DELETE":
        try:
            financial_id = request.args.get("id")
            financial = db.session.query(Financial).get(financial_id)
            
            if not financial:
                return jsonify({"error": "Financial record not found"}), 404
            
            db.session.delete(financial)
            db.session.commit()
            return jsonify({"message": "Financial record deleted successfully"}), 200
        except Exception as e:
            return jsonify({"error": "Internal server error"}), 500

    return jsonify({"message": "Method not implemented"}), 501
