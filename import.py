import csv
import os

from app import app, db
from app.models import Product

def main():
    with app.app_context():  
        # Import Products from CSV File
        with open("products.csv", newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for name, vitamin, flavour, price, description in reader:
                # Check if Product Already Exists Based On Name
                product = Product.query.filter_by(name=name).first()

                if product:
                    # If Product Exists, Update Fields that have Changed
                    product.vitamin = vitamin
                    product.flavour = flavour
                    product.price = price
                    product.description = description
                    print(f"Updated product: {name}")
                else:
                    # If Product Doesn't Exist, Add to Table
                    product = Product(name=name, vitamin=vitamin, flavour=flavour, price=price, description=description)
                    db.session.add(product)
                    print(f"Added product: {name}")

        db.session.commit()

if __name__ == "__main__":
    main()