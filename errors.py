from flask import Blueprint, render_template
from app import db

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title="Error"), 404

@errors.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', title="Error"), 500