from app import app, db
from app.models import User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
    # Check if Admin Already Exists
        admin = User.query.filter_by(email='katie@admin.com').first()

        if not admin:
            # Create Admin if not Already Created
            admin = User(
                firstname='Katie',
                lastname='Admin',
                email='katie@admin.com',
                password_hash=generate_password_hash('pa55word')
            )
            admin.is_admin = True
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    create_admin()
