from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from CRM.config import Config
from dotenv import load_dotenv


load_dotenv()
db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # init extensions
    db.init_app(app)

    # register blueprints
    from CRM.endpoints.main.routes import main_bp
    from CRM.endpoints.api.routes import api_bp
    from CRM.endpoints.customers.routes import customers_bp
    from CRM.endpoints.services.routes import services_bp
    from CRM.endpoints.financials.routes import financials_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(financials_bp)
    return app
