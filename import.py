import csv
import os

from app import app, db
from app.models import Product

def main():
    with app.app_context():  
        with open("products.csv", newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for name, vitamin, flavour, price, description in reader:
                # Check if the product already exists based on the name (or another unique field)
                product = Product.query.filter_by(name=name).first()

                if product:
                    # If the product exists, update the fields that may have changed
                    product.vitamin = vitamin
                    product.flavour = flavour
                    product.price = price
                    product.description = description
                    print(f"Updated product: {name}")
                else:
                    # If the product doesn't exist, create a new one
                    product = Product(name=name, vitamin=vitamin, flavour=flavour, price=price, description=description)
                    db.session.add(product)
                    print(f"Added product: {name}")

        db.session.commit()

if __name__ == "__main__":
    main()