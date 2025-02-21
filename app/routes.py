from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from app import app
from app.forms import LoginForm, RegistrationForm, UpdateAccountForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User, Product, Cart
from urllib.parse import urlsplit


@app.route('/')
def home():
    return render_template('main.html', title='Home')

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.lastname = form.lastname.data
        current_user.firstname = form.firstname.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.lastname.data = current_user.lastname
        form.firstname.data = current_user.firstname
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('You are logged in!')
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(lastname=form.lastname.data,firstname=form.firstname.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/shop')
def shop():
    page = request.args.get("page", 1, type=int)
    per_page = 8  # Display 8 products per page
    products = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template("shop.html", title="Shop", products=products.items, pagination=products)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)  # Fetch product or show 404
    return render_template("product.html", product=product)


@app.route("/addToCart/<int:product_id>", methods=["POST"])
@login_required
def addToCart(product_id):
    # Get the quantity from the request, default to 1 if not provided
    quantity = request.form.get("quantity", 1)  # Assuming you have a quantity field in your form

    # Check if product is already in the cart
    cart_item = Cart.query.filter_by(product_id=product_id, user_id=current_user.id).first()

    if cart_item:
        # If the product is already in the cart, update the quantity
        cart_item.quantity += int(quantity)
        db.session.commit()
        message = f"{quantity} more added to your cart!"
    else:
        # If the product is not in the cart, add it with the selected quantity
        new_cart_item = Cart(user_id=current_user.id, product_id=product_id, quantity=int(quantity))
        db.session.add(new_cart_item)
        db.session.commit()
        message = "Item added to cart!"

    return jsonify({"message": message})


@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    # Get the user's cart items
    cart_items = Cart.query.join(Product).filter(Cart.user_id == current_user.id).all()

    # Calculate the subtotal
    subtotal = sum(item.product.price * item.quantity for item in cart_items)

    # Handle POST requests for updating quantities (if you have that functionality)
    if request.method == "POST":
        qty = request.form.get("qty")
        product_id = request.form.get("product_id")
        cart_item = Cart.query.filter_by(product_id=product_id, user_id=current_user.id).first()

        if cart_item:
            cart_item.quantity = qty
            db.session.commit()

    return render_template('cart.html', cart_items=cart_items, subtotal=subtotal)

@app.route("/cart/update_quantity/<int:item_id>", methods=["POST"])
@login_required
def update_quantity(item_id):
    action = request.form.get("action")
    cart_item = Cart.query.get(item_id)
    
    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease" and cart_item.quantity > 1:
        cart_item.quantity -= 1
    
    db.session.commit()
    return redirect(url_for('cart'))

@app.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove(item_id):
    cart_item = Cart.query.get(item_id)
    if cart_item and cart_item.user_id == current_user.id:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from your cart!', 'success')
    return redirect(url_for('cart'))