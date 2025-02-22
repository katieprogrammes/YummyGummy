from flask import render_template, flash, redirect, url_for, request, jsonify, abort, make_response
from app import app
from app.forms import LoginForm, RegistrationForm, UpdateAccountForm, ContactForm
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User, Product, Cart
from urllib.parse import urlsplit
from flask_mail import Mail, Message


mail = Mail(app)


@app.route('/')
def home():
    return render_template('main.html', title='Home')

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')


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
            flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))
    
    elif request.method == 'GET':
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.email.data = current_user.email

    return render_template('updateaccount.html', title='Edit Account', form=form)
    
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
    data = request.get_json()
    quantity = data.get("quantity", 1)

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

    return jsonify({'status': 'success', 'message': message})

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

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        email = form.email.data
        order_no = form.order_no.data
        message = form.message.data
        flash("Message sent successfully!", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html", form=form)

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

    return render_template('search_results.html', results=results, query=query)

@app.route('/filter-sort', methods=['GET'])
def filter_sort():
    sort_by = request.args.get('sort_by', 'name_asc')
    filter_vitamin = request.args.get('vitamin', '')
    filter_flavour = request.args.get('flavour', '')
    filter_price_min = request.args.get('price_min', None)
    filter_price_max = request.args.get('price_max', None)
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
                Product.flavour.ilike(f"%{query}%")
            )
        )

    # Apply filters
    if filter_vitamin:
        products_query = products_query.filter(Product.vitamin.ilike(f"%{filter_vitamin}%"))
    if filter_flavour:
        products_query = products_query.filter(Product.flavour.ilike(f"%{filter_flavour}%"))
    if filter_price_min:
        products_query = products_query.filter(Product.price >= float(filter_price_min))
    if filter_price_max:
        products_query = products_query.filter(Product.price <= float(filter_price_max))

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
                           filter_price_max=filter_price_max)