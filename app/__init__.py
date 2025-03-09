from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

# Importing and Registering Existing Routes and Models
from app import routes, models

# Registering Error Handlers
from errors import errors as errors_bp
app.register_blueprint(errors_bp)

# Importing and Registering API Blueprint
from app.api.routes import api_bp
app.register_blueprint(api_bp, url_prefix="/api") 