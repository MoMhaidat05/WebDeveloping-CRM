from CRM import create_app, db
from CRM.models import *

app = create_app()

if __name__ == "__main__":
    app.run(port=8080)
