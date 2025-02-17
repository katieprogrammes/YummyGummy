import csv
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from app import app, db
from app.models import Product

def main():
    with app.app_context():  
        with open("products.csv", newline="") as f:
            reader = csv.reader(f)
            for name, vitamin, flavour, price in reader:
                product = Product(name=name, vitamin=vitamin, flavour=flavour, price=price)
                db.session.add(product)
                print(f"Added product: {name}, {vitamin}, {flavour}, {price}")
        db.session.commit()

if __name__ == "__main__":
    main()