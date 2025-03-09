from flask import Blueprint, render_template, flash, redirect, url_for, jsonify
from flask_login import current_user
from app import db

errors = Blueprint('errors', __name__)

# 404 Error
@errors.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title="Error"), 404

# 500 Error
@errors.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', title="Error"), 500

# 401 Error
@errors.app_errorhandler(401)
def unauthorised_error(error):
    # For API
    if current_user.is_authenticated:
        return jsonify({"error": "Unauthorized action. Please log in."}), 401
    else:
        # For app.routes
        flash("Please Login!", "custom-success")
        return redirect(url_for("login"))