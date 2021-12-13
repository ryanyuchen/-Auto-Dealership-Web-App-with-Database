from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, NumberRange
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, IntegerField, FloatField, \
    SelectMultipleField, DateField
from wtforms.fields.html5 import DateField


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=25)])
    submit = SubmitField('Login')


class SearchForm(FlaskForm):
    manufacturerName = SelectField('Manufacturer', choices=[])
    vehicleType = SelectField('Vehicle Type', choices=['Car', 'Truck', 'SUV', 'Van', 'Convertible'])
    color = SelectField('Color', choices=['Aluminum', 'Beige', 'Black', 'Blue', 'Brown', 'Bronze', 'Claret', 'Copper',
                                          'Cream', 'Gold', 'Gray', 'Green', 'Maroon', 'Metallic', 'Navy', 'Orange',
                                          'Pink', 'Purple', 'Red', 'Rose', 'Rust', 'Silver', 'Tan', 'Turquoise',
                                          'White', 'Yellow'])
    modelYear = SelectField('Model Year', choices=[year for year in range(1900, 2023)])
    listPrice = SelectField('List Price', choices=[price for price in range(1000, 50001, 1000)])
    keyword = StringField('Keyword', validators=[Length(max=500)])
    submit = SubmitField('Search')


class searchByVinForm(FlaskForm):
    vin = StringField('VIN', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Enter')


class searchByFilterForm(FlaskForm):
    filter = SelectField('Vehicle Status', choices=['All Vehicles', 'Sold Vehicles', 'Unsold Vehicles'])
    submit = SubmitField('Search')


class IndividualForm(FlaskForm):
    DL_number = StringField("Driver License Number", validators=[DataRequired(), Length(min=2, max=50)])
    individual_first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=50)])
    individual_last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email Address", validators=[Email()])
    phone_number = StringField("Phone Number", validators=[DataRequired(), Length(min=2, max=50)])
    street = StringField("Street", validators=[DataRequired(), Length(max=50)])
    city = StringField("City", validators=[DataRequired(), Length(max=50)])
    state = StringField("State", validators=[DataRequired(), Length(min=2, max=50)])
    postal_code = StringField("Postal Code", validators=[DataRequired(), Length(min=5, max=50)])
    submit = SubmitField('Submit')


class BusinessForm(FlaskForm):
    TIN_number = StringField("Tax Identification Number", validators=[DataRequired(), Length(min=2, max=50)])
    business_name = StringField("Business Name", validators=[DataRequired(), Length(min=2, max=50)])
    pc_first_name = StringField("Primary Contact First Name", validators=[DataRequired(), Length(min=2, max=50)])
    pc_last_name = StringField("Primary Contact Last Name", validators=[DataRequired(), Length(min=2, max=50)])
    pc_title = StringField("Primary Contact Title", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email Address", validators=[Email()])
    phone_number = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=50)])
    street = StringField("Street", validators=[DataRequired(), Length(max=50)])
    city = StringField("City", validators=[DataRequired(), Length(max=50)])
    state = StringField("State", validators=[DataRequired(), Length(min=2, max=50)])
    postal_code = StringField("Postal Code", validators=[DataRequired(), Length(min=5, max=50)])
    submit = SubmitField('Submit')


class addNewVehicleForm(FlaskForm):
    vin = StringField('vin', validators=[DataRequired(), Length(min=2, max=50)])
    manufacturer = StringField('Manufacturer', validators=[DataRequired()])
    modelName = StringField('Model Name', validators=[DataRequired()])
    modelYear = SelectField('Model Year', choices=[year for year in range(1900, 2023)], validators=[DataRequired()])
    vehicleType = SelectField('Vehicle Type', choices=['Choose vehicle type', 'Car', 'Truck', 'SUV', 'Van', 'Convertible'], validators=[DataRequired()])
    description = StringField('Description')
    invoicePrice = FloatField('Invoice Price', validators=[DataRequired(), NumberRange(min=0)])

    numberOfDoors = IntegerField('Number Of Doors', validators=[NumberRange(min=0, max=25), DataRequired()], default=0)

    roofType = StringField('Roof Type', validators=[DataRequired()], default='Enter vehicle type')
    backSeatCount = IntegerField('Back Seat Count', validators=[NumberRange(min=0, max=25), DataRequired()], default=0)

    cargoCapacity = FloatField('Cargo Capacity(in tons)', validators=[NumberRange(min=0), DataRequired()], default=0)
    noOfRearAxles = IntegerField('Number Of Rear Axles', validators=[NumberRange(min=0, max=25), DataRequired()], default=0)
    cargoCoverType = StringField('Cargo Cover Type', validators=[DataRequired()], default='Enter Cargo Cover Type')

    noOfCupHolders = IntegerField('Number Of Cup Holders', validators=[NumberRange(min=0, max=25), DataRequired()], default=0)
    drivetrainType = StringField('Drivetrain Type', validators=[DataRequired()], default='Enter Drivetrain Type')

    hasBackDoor = SelectField('Has Driver’s Side Back Door', choices=['0', '1'])

    # colors = SelectMultipleField('Color', choices=['Aluminum', 'Beige', 'Black', 'Blue', 'Brown', 'Bronze', 'Claret',
    #                                                 'Copper', 'Cream', 'Gold', 'Gray', 'Green', 'Maroon', 'Metallic',
    #                                                'Navy', 'Orange', 'Pink', 'Purple', 'Red', 'Rose', 'Rust', 'Silver',
    #                                                'Tan', 'Turquoise',
    #                                                 'White', 'Yellow'], validators=[DataRequired()])
    colors = SelectMultipleField('Color', choices=[('Aluminum', 'Aluminum'), ('Beige', 'Beige'), ('Black', 'Black'),
                                                   ('Blue', 'Blue'), ('Brown', 'Brown'), ('Bronze', 'Bronze'),
                                                   ('Claret', 'Claret'), ('Copper', 'Copper'), ('Cream', 'Cream'),
                                                   ('Gold', 'Gold'), ('Gray', 'Gray'), ('Green', 'Green'),
                                                   ('Maroon', 'Maroon'), ('Metallic', 'Metallic'), ('Navy', 'Navy'),
                                                   ('Orange', 'Orange'), ('Pink', 'Pink'), ('Purple', 'Purple'),
                                                   ('Red', 'Red'), ('Rose', 'Rose'), ('Rust', 'Rust'),
                                                   ('Silver', 'Silver'), ('Tan', 'Tan'), ('Turquoise', 'Turquoise'),
                                                   ('White', 'White'), ('Yellow', 'Yellow')], validators=[DataRequired()])
    submit = SubmitField('Save')


class salesOrderForm(FlaskForm):
    price = FloatField("price", validators=[DataRequired(), NumberRange(min=0)])
    purchaseDate = DateField('purchaseDate', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Submit')

