from datetime import datetime
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
from CRM import db 

load_dotenv()

class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(50)) 
    phone_primary = db.Column(db.String(20), nullable=False)
    phone_secondary = db.Column(db.String(20))
    email = db.Column(db.String(120))
    business_name = db.Column(db.String(150))
    city = db.Column(db.String(50), default='Aqaba')
    location_url = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.now())

    services = db.relationship('Service', backref='client', lazy=True, cascade="all, delete-orphan")
    financials = db.relationship('Financial', backref='client', lazy=True, cascade="all, delete-orphan")
    logs = db.relationship('ActivityLog', backref='client', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client {self.nickname} - {self.business_name}>"

class Service(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    domain_name = db.Column(db.String(150), nullable=False)
    domain_registrar = db.Column(db.String(50))
    domain_expiry_date = db.Column(db.Date)
    
    hosting_provider = db.Column(db.String(50))
    server_ip = db.Column(db.String(50))
    ssh_port = db.Column(db.Integer, default=22)
    hosting_expiry_date = db.Column(db.Date)
    
    tech_stack = db.Column(db.String(100))

    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    credentials = db.relationship('Credential', backref='service', lazy=True, cascade="all, delete-orphan")


class Financial(db.Model):
    __tablename__ = 'financials'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    project_title = db.Column(db.String(150)) 
    total_amount = db.Column(db.Float, default=0.0)
    paid_amount = db.Column(db.Float, default=0.0)
    renewal_price = db.Column(db.Float, default=0.0)
    
    next_renewal_date = db.Column(db.Date) 
    last_payment_date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.now())
    
    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_amount

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    
    action_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now())