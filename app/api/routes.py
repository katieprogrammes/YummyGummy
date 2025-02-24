from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Product, Cart


#Creating a Blueprint for the API
api_bp = Blueprint("api", __name__)

@api_bp.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    product_list = [{
        "id": product.id,
        "name": product.name,
        "vitamin": product.vitamin,
        "flavour": product.flavour,
        "price": product.price,
        "description": product.description
    } for product in products]

    return jsonify({"products": product_list})

@api_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)

    product_data = {
        "id": product.id,
        "name": product.name,
        "vitamin": product.vitamin,
        "flavour": product.flavour,
        "price": product.price,
        "description": product.description
    }

    return jsonify({"product": product_data})


@api_bp.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    if request.method == "GET":
        cart_items = Cart.query.join(Product).filter(Cart.user_id == current_user.id).all()
        subtotal = sum(item.product.price * item.quantity for item in cart_items)

        return jsonify({
            'cart_items': [{"product_id": item.product.id, "name": item.product.name, "quantity": item.quantity} for item in cart_items],
            'subtotal': subtotal
        })

    elif request.method == "POST":
        data = request.get_json()
        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)

        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400

        cart_item = Cart.query.filter_by(product_id=product_id, user_id=current_user.id).first()
        if cart_item:
            cart_item.quantity += int(quantity)
        else:
            new_cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=int(quantity))
            db.session.add(new_cart_item)

        db.session.commit()
        return jsonify({"message": "Cart updated successfully!"}), 200



@api_bp.route("/cart/add", methods=["POST"])
@login_required
def add_to_cart():
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    cart_item = Cart.query.filter_by(product_id=product_id, user_id=current_user.id).first()
    if cart_item:
        cart_item.quantity += int(quantity)
    else:
        new_cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=int(quantity))
        db.session.add(new_cart_item)

    db.session.commit()
    return jsonify({"message": "Item added to cart!"}), 200




@api_bp.route("/cart/remove/<int:item_id>", methods=["DELETE"])
@login_required
def remove_from_cart(item_id):
    cart_item = Cart.query.get(item_id)
    if not cart_item or cart_item.user_id != current_user.id:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Item removed from cart!"}), 200


@api_bp.route("/cart/update_quantity/<int:item_id>", methods=["PUT"])
@login_required
def update_quantity(item_id):
    data = request.get_json()
    quantity = data.get("quantity")
    
    if quantity is None:
        return jsonify({"error": "Quantity is required"}), 400

    cart_item = Cart.query.get(item_id)
    if not cart_item or cart_item.user_id != current_user.id:
        return jsonify({"error": "Item not found"}), 404

    cart_item.quantity = quantity
    db.session.commit()
    return jsonify({"message": "Cart item quantity updated!"}), 200
