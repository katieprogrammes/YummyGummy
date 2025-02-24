from flask import Blueprint

api = Blueprint('api', __name__)

from app import routes 