from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from app import login
from flask import flash

# User Model
class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    firstname: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    lastname: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), unique=True, nullable=False)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=False)

    # Hashing the Password for Security
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Password Matching Checker
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"User('{self.firstname}','{self.lastname}', '{self.email}','{self.id}')"
    
    # Adding to Cart
    def add_to_cart(self,product_id):
        item_to_add = Cart(product_id=product_id, user_id=self.id)
        db.session.add(item_to_add)
        db.session.commit()
        flash('Your item has been added to your cart!', 'success')

# Login Logic
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


# Product Model
class Product(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(255), index=True, nullable=False)
    vitamin: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    flavour: so.Mapped[str] = so.mapped_column(sa.String(50), index=True, nullable=True)
    price: so.Mapped[float] = so.mapped_column(sa.Numeric(10, 2), nullable=False)
    description: so.Mapped[str] = so.mapped_column(sa.String(1000), nullable=True)




    def __repr__(self):
        return f"Products('{self.name}','{self.price}')"
    

#Cart Model
class Cart(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    product_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('product.id'), nullable=False)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)
    quantity: so.Mapped[int] = so.mapped_column(nullable=False, default=1)

    product = db.relationship('Product', backref='carts', lazy=True)

    #Calculate Cart Price for Items
    @property
    def total_price(self):
        return self.product.price * self.quantity
    
    
    def __repr__(self):
        return f"Cart('Product id:{self.product_id}','id: {self.id}','User id:{self.user_id}'')"


# Wishlist Model
class Wishlist(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    product_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('product.id'), nullable=False)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)


    product = db.relationship('Product', backref='wishlist', lazy=True)
    
    
    def __repr__(self):
        return f"Cart('Product id:{self.product_id}','id: {self.id}','User id:{self.user_id}'')"