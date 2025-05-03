# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Email

# Form for manager registration
class ManagerForm(FlaskForm):
    ssn = StringField('SSN', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Register')

# Form for client registration (including address and credit card)
class ClientForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    # Address fields (allow multiple addresses in the UI)
    address_road = StringField('Road', validators=[DataRequired()])
    address_number = StringField('Number', validators=[DataRequired()])
    address_city = StringField('City', validators=[DataRequired()])
    # Credit card fields
    credit_card_number = StringField('Credit Card Number', validators=[DataRequired()])
    credit_card_road = StringField('Credit Card Road', validators=[DataRequired()])
    credit_card_number_field = StringField('Credit Card Number (Address)', validators=[DataRequired()])  # Renamed for clarity
    credit_card_city = StringField('Credit Card City', validators=[DataRequired()])
    submit = SubmitField('Register')

# Form for adding a car
class CarForm(FlaskForm):
    carid = StringField('Car ID', validators=[DataRequired()])
    brand = StringField('Brand', validators=[DataRequired()])
    submit = SubmitField('Add Car')

# Form for adding a model
class ModelForm(FlaskForm):
    carid = StringField('Car ID', validators=[DataRequired()])
    color = StringField('Color', validators=[DataRequired()])
    construction_year = StringField('Construction Year', validators=[DataRequired()])
    transmission = StringField('Transmission', validators=[DataRequired()])
    submit = SubmitField('Add Model')

# Form for adding a driver
class DriverForm(FlaskForm):
    drivername = StringField('Driver Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address_road = StringField('Road', validators=[DataRequired()])
    address_number = StringField('Number', validators=[DataRequired()])
    address_city = StringField('City', validators=[DataRequired()])
    submit = SubmitField('Add Driver')


# Form for viewing available models and booking a rent
class RentForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    carid = SelectField('Car Model', choices=[], coerce=int, validators=[DataRequired()])
    submit_view = SubmitField('View Available Models')
    submit_book = SubmitField('Book Rent')
