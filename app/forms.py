from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Optional
import sqlalchemy as sa
from app import db
from app.models import User

# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# Registration Form
class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match")])
    submit = SubmitField('Register')

# Checks if Email Already Exists
def validate_email(self, email):
    user = db.session.scalar(sa.select(User).where(
        User.email  == email.data))
    if user is not None:
        raise ValidationError('This email is already registered. Please login')

# Update Account Form
class UpdateAccountForm(FlaskForm):
    firstname = StringField('First Name',validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

# Contact Form
class ContactForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    order_no = StringField("Order No (Optional)", validators=[Optional()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send")

#Newsletter Form
class NewsletterForm(FlaskForm):
    email = StringField("Please enter your Email", validators=[DataRequired(), Email()])
    tandc = BooleanField('Send me emails about new products, savings and more')
    submit = SubmitField("Subscribe")