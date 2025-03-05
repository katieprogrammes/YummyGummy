from flask import render_template, flash, redirect, url_for, request, jsonify, abort, make_response
from app import app
from app.forms import LoginForm, RegistrationForm, UpdateAccountForm, ContactForm, NewsletterForm
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import or_, and_
import sqlalchemy as sa
from app import db
from app.models import User, Product, Cart, Wishlist
from urllib.parse import urlsplit
from flask_mail import Mail, Message
import requests
from config import Config

mail = Mail(app)


@app.route('/', methods=['GET', 'POST'])
def home():
    form = NewsletterForm()
    if form.validate_on_submit():
        email = form.email.data
        flash("Thankyou for subscribing, check your emails for your discount code!", "custom-success")
        return redirect(url_for("home"))

    return render_template('main.html', form=form, title='Home')

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')

@app.route('/faq')
def faq():
    return render_template('faq.html', title='FAQ')


@app.route('/editaccount', methods=['GET', 'POST'])
@login_required
def editaccount():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        # Check if the email is already in use by another user
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Email is already in use. Please choose a different one.', 'danger')
        else:
            current_user.firstname = form.firstname.data
            current_user.lastname = form.lastname.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'custom-success')
            return redirect(url_for('account'))
    
    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.email.data = current_user.email

    return render_template('updateaccount.html', title='Edit Account', form=form)
    
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'custom-success')
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
        flash('You are logged in!', 'custom-success')
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
        flash('Congratulations, you are now a registered user!', 'custom-success')
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
    return render_template("product.html", product=product, title=product.name)


@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    if request.method == "GET":
        # Get the user's cart items
        cart_items = Cart.query.join(Product).filter(Cart.user_id == current_user.id).all()

        # Calculate the subtotal
        subtotal = sum(item.product.price * item.quantity for item in cart_items)

        # Render the cart page template
        return render_template("cart.html", title="Cart", cart_items=cart_items, subtotal=subtotal)

    # Handle POST requests for updating quantities
    elif request.method == "POST":
        qty = request.form.get("qty")
        product_id = request.form.get("product_id")
        cart_item = Cart.query.filter_by(product_id=product_id, user_id=current_user.id).first()

        if cart_item:
            cart_item.quantity = qty
            db.session.commit()

        
        return jsonify({'status': 'custom-success', 'message': 'Cart updated!'})


@app.route("/cart/update_quantity/<int:item_id>", methods=["POST"])
@login_required
def update_quantity(item_id):
    action = request.form.get("action")
    api_url = f"{Config.API_BASE_URL}/cart/update_quantity/{item_id}"
    response = requests.post(api_url, json={"action": action})
    
    if response.status_code == 200:
        flash(response.json()["message"], "custom-success")
    else:
        flash(response.json().get("error", "An error occurred"), "danger")

    return redirect(url_for('cart'))

@app.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove(item_id):
    api_url = f"{Config.API_BASE_URL}/cart/{item_id}"
    response = requests.delete(api_url)

    # Handle the response from the API
    if response.status_code == 200:
        flash(response.json()["message"], "custom-success")
    else:
        flash(response.json().get("error", "An error occurred"), "danger")
    return redirect(url_for('cart'))

@app.route("/wishlist", methods=["GET", "POST"])
@login_required
def wishlist():
    if request.method == "GET":
        # Get the user's wishlist items
        wish_items = Wishlist.query.join(Product).filter(Wishlist.user_id == current_user.id).all()


        # Render the wishlist template
        return render_template("wishlist.html", title="Wishlist", wish_items=wish_items)
    
    elif request.method == "POST":
        data = request.get_json()
        product_id = data.get("product_id")

        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400
        
        # Check if product already exists in the wishlist
        existing_item = Wishlist.query.filter_by(product_id=product_id, user_id=current_user.id).first()

        if existing_item:
            return jsonify({"message": "This item is already in your wishlist"}), 400
        else:
            # Add the product to the wishlist
            new_wish_item = Wishlist(user_id=current_user.id, product_id=product_id)
            db.session.add(new_wish_item)

        db.session.commit()
        return jsonify({"message": "Item added to wishlist!"}), 200
    

@app.route("/wishlist/remove/<int:item_id>", methods=["DELETE"])
@login_required
def remove_wish(item_id):
    # Log the item removal attempt
    print(f"Attempting to remove item with ID: {item_id}")
    
    # Call to API
    api_url = f"{Config.API_BASE_URL}/wishlist/{item_id}"
    response = requests.delete(api_url)

    # Log the raw response text to debug the issue
    print(f"API response: {response.text}")

    # Handle the response from the API
    if response.status_code == 200:
        flash(response.json().get("message", "Item removed from wishlist"), "custom-success")
    else:
        flash(response.json().get("error", "An error occurred"), "danger")

    # Redirect to the wishlist page after item removal
    return redirect(url_for('wishlist'))



@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        email = form.email.data
        order_no = form.order_no.data
        message = form.message.data
        flash("Message sent successfully!", "custom-success")
        return redirect(url_for("contact"))

    return render_template("contact.html", form=form, title="Contact Us")

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    
    if query:
        results = Product.query.filter(
            db.or_(
                Product.name.ilike(f"%{query}%"),
                Product.vitamin.ilike(f"%{query}%"),
                Product.flavour.ilike(f"%{query}%")
            )
        ).all()
    else:
        results = []

    return render_template('search_results.html', results=results, query=query, title="Shop")

@app.route('/filter-sort', methods=['GET'])
def filter_sort():
    sort_by = request.args.get('sort_by', 'name_asc')
    filter_vitamin = request.args.get('vitamin', '').strip()
    filter_flavour = request.args.get('flavour', '').strip()
    filter_price_min = request.args.get('price_min', type=float)
    filter_price_max = request.args.get('price_max', type=float)
    query = request.args.get('q', '').strip() 
    page = request.args.get('page', 1, type=int)
    per_page = 8

    # Base query for filtering and sorting
    products_query = Product.query

    # If a search query exists, filter by that query as well
    if query:
        products_query = products_query.filter(
            db.or_(
                Product.name.ilike(f"%{query}%"),
                Product.vitamin.ilike(f"%{query}%"),
                Product.flavour.ilike(f"%{query}%"),
                Product.description.ilike(f"%{query}%")
            )
        )

    # Apply filters
    if filter_vitamin:
        products_query = products_query.filter(Product.vitamin.ilike(f"%{filter_vitamin}%"))
    if filter_flavour:
        products_query = products_query.filter(Product.flavour.ilike(f"%{filter_flavour}%"))
    if filter_price_min is not None:
        products_query = products_query.filter(Product.price >= filter_price_min)
    if filter_price_max is not None:
        products_query = products_query.filter(Product.price <= filter_price_max)

    


    # Apply sorting
    if sort_by == 'name_asc':
        products_query = products_query.order_by(Product.name.asc())
    elif sort_by == 'name_desc':
        products_query = products_query.order_by(Product.name.desc())
    elif sort_by == 'price_asc':
        products_query = products_query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        products_query = products_query.order_by(Product.price.desc())


    pagination = products_query.paginate(page=page, per_page=per_page, error_out=False)
    results = pagination.items


    return render_template('filter_sort_results.html', 
                           results=results,
                           pagination=pagination,
                           query=query,  
                           sort_by=sort_by,
                           filter_vitamin=filter_vitamin,
                           filter_flavour=filter_flavour,
                           filter_price_min=filter_price_min,
                           filter_price_max=filter_price_max,
                            title="Shop")