import csv
import os
from app import app, db
from app.models import Product
import sys

def main(file_path):
    with app.app_context():  
        # Import Products from CSV File
        csv_product_names = set()
        with open(file_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for name, vitamin, flavour, price, description in reader:
                csv_product_names.add(name)

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

        # Delete products that are not in the CSV
        existing_products = Product.query.all()
        for product in existing_products:
            if product.name not in csv_product_names:
                db.session.delete(product)
                print(f"Deleted product: {product.name}")

        db.session.commit()

if __name__ == "__main__":
    file_path = sys.argv[1]
    main(file_path)