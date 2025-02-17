from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
from app import login

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    firstname: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    lastname: so.Mapped[str] = so.mapped_column(sa.String(64), nullable=False)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), unique=True, nullable=False)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), nullable=False)

    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"User('{self.firstname}','{self.lastname}', '{self.email}','{self.id}')"

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

product_vitamin = db.Table(
    "product_vitamin",
    db.Column("product_id", sa.Integer, sa.ForeignKey("product.id"), primary_key=True),
    db.Column("vitamin_id", sa.Integer, sa.ForeignKey("vitamin.id"), primary_key=True),
)



class Product(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[int] = so.mapped_column(sa.String(255), index=True, nullable=False)
    flavour: so.Mapped[str] = so.mapped_column(sa.String(50), index=True, nullable=True)
    price: so.Mapped[float] = so.mapped_column(sa.Numeric(10, 2), nullable=False)
    stock: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False, default=0)

        # Relationship to vitamins (many-to-many)
    vitamins: so.Mapped[list["Vitamin"]] = so.relationship(
        "Vitamin", secondary=product_vitamin, back_populates="products"
    )

    def __repr__(self):
        return f"<Product {self.name} - {len(self.vitamins)} Vitamins>"

class Vitamin(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), unique=True, nullable=False)
    
    # Relationship to products (many-to-many)
    products: so.Mapped[list["Product"]] = so.relationship(
        "Product", secondary=product_vitamin, back_populates="vitamins"
    )

    def __repr__(self):
        return f"<Vitamin {self.name}>"