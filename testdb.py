from app import app, db
from app.models import Product

with app.app_context():
    # Remove duplicates based on 'name' (or another unique field)
    duplicates = db.session.query(Product.name, db.func.count(Product.id)).group_by(Product.name).having(db.func.count(Product.id) > 1).all()

    for duplicate in duplicates:
        name = duplicate[0]

        # Get all rows for this name
        products = Product.query.filter_by(name=name).all()

        # Keep the first product and delete the others
        for product in products[1:]:
            db.session.delete(product)

    db.session.commit()
