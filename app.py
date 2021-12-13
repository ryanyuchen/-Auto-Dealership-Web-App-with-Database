from flask import Flask, redirect, url_for, render_template, session, request, flash
from flask_mysqldb import MySQL
from forms import LoginForm, SearchForm, searchByVinForm, searchByFilterForm, IndividualForm, BusinessForm, \
    addNewVehicleForm, salesOrderForm
from sql.JJ_sql import JJQuery
import datetime
from datetime import datetime
import numbers

app = Flask(__name__)

# Set secret key for user login
app.secret_key = 'Team045_private'
# app.config['SECRET_KEY'] = 'Team045_private'

# configure local database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'gatechUser'
app.config['MYSQL_PASSWORD'] = 'gatech123'
app.config['MYSQL_DB'] = 'cs6400_fa21_team045'
mysql = MySQL(app)

# Create sql query instance to access all queries
JJQuery = JJQuery()


@app.route('/', methods=['GET', 'POST'])
def home():
    search_form = SearchForm()
    search_by_vin_form = searchByVinForm()
    search_by_filter_form = searchByFilterForm()

    cursor = mysql.connection.cursor()
    # get number of vehicles
    cursor.execute(JJQuery.count_number_of_vehicles)
    count = cursor.fetchone()

    # get list of manufacturer names
    # if "all_manufacturers" not in session:
    cursor.execute(JJQuery.get_manufacturer_name)
    session["last_page"] = "home"
    session["all_manufacturers"] = [name[0] for name in cursor.fetchall()]
    search_form.manufacturerName.choices = session["all_manufacturers"]

    return render_template("home.html", count=count[0], form=search_form, form2=search_by_vin_form,
                           form3=search_by_filter_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute(JJQuery.validate_user, (username,))
        user = cursor.fetchone()
        if user and password == user[0]:
            session["dateNow"] = datetime.now().strftime("%Y-%m-%d")
            session['username'] = username
            cursor.execute(JJQuery.find_user_role, (username,))
            role = cursor.fetchone()
            session['role'] = role[2]
            flash(f"Login successful! Welcome, {username} !", "login")
            return redirect(url_for('home'))
        else:
            message = 'Wrong username or password'
            return render_template("login.html", title='Login', form=form, msg=message)
    else:
        if "username" in session:
            flash("Already Logged In !")
            return redirect(url_for('home'))
        return render_template("login.html", title='Login', form=form)


@app.route('/logout')
def logout():
    if 'username' in session:
        username = session["username"]
        flash(f"You have logged out, {username}", "logout")

    session.pop("username", None)
    session.pop("role", None)
    session.pop("VIN", None)
    session.pop("customer", None)
    session.pop("vehicle_details", None)
    session.pop("vehicle_type", None)
    session.pop("unfinished_repair", None)
    session.pop("dateNow", None)
    session.pop("last_page", None)
    return redirect(url_for('home'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        session["last_page"] = "search"
        if 'vehicle_search' in request.form:
            res_manufacturer = request.form.get("res_manufacturer")
            res_type = request.form.get("res_type")
            res_year = request.form.get("res_year")
            res_color = request.form.get("res_color")
            res_price_range = request.form.get("res_price_range")
            res_keyword = request.form['keyword']

            res = {
                'res_manufacturer': res_manufacturer,
                'res_type': res_type,
                'res_year': res_year,
                'res_color': res_color,
                'res_price_range': res_price_range.split()[2],
                'res_keyword': "%" + res_keyword + "%"
            }

            cursor.execute(JJQuery.get_selected_unsold_vehicles, res)
            unsold_vehicles = cursor.fetchall()

            # unsold_vehicles = []
            # for i in res_unsold_vehicles:
            #     line = tuple(["%.2f" % round(x, 2) if isinstance(x, float) else x for x in i])
            #     unsold_vehicles.append(line)

            # print("# of matched records: ", len(unsold_vehicles))
            # for line in unsold_vehicles:
            #     print(line)

            # Show vehicle not found message for empty result
            if len(unsold_vehicles) == 0:
                flash("Sorry, it looks like we don’t have that in stock!")
                return redirect(url_for('home'))
            else:
                return render_template('search.html', selected_vehicles_table=unsold_vehicles, keyword=res_keyword)

        if 'search_by_vin' in request.form:
            vin = request.form['vin']
            cursor.execute(JJQuery.get_vehicles_by_vin, [vin, ])
            res_vin = cursor.fetchone()

            if res_vin:
                vehicle_type = res_vin[1]
                return redirect(url_for('detail', vin=vin, type=vehicle_type))
            # Show vehicle not found message for empty result
            else:
                flash("Sorry, it looks like we don’t have that car!")
                return redirect(url_for('home'))

        if 'search_by_vin_in_repair' in request.form:
            vin = request.form['vin']
            cursor.execute(JJQuery.get_vehicles_by_vin, [vin, ])
            res_vin = cursor.fetchone()
            if res_vin:
                if res_vin[8] == "Sold":
                    vehicle_type = res_vin[1]
                    session["customer"] = None
                    return redirect(url_for('repairDetail', vin=vin, type=vehicle_type))
                # Show vehicle not found message for empty result
                elif res_vin[8] == "Unsold":
                    flash("This vehicle is currently unsold!")
                    return redirect(url_for('repair'))
            else:
                flash("Sorry, it looks like we don’t have that car!")
                return redirect(url_for('repair'))

        if 'search_by_filter' in request.form:
            filter = {"filter": request.form['filter']}

            cursor.execute(JJQuery.get_vehicles_by_filter, filter)
            filtered_vehicles = cursor.fetchall()

            # filtered_vehicles = []
            # for i in res_filtered_vehicles:
            #     line = tuple(["%.2f" % round(x, 2) if isinstance(x, float) else x for x in i])
            #     filtered_vehicles.append(line)

            if filtered_vehicles:
                return render_template('search.html', selected_vehicles_table=filtered_vehicles, keyword="")
            else:
                flash("Sorry, it looks like we don’t have that car!")
                return redirect(url_for('home'))


@app.route('/search/vin=<string:vin>/type=<string:type>', methods=['GET', 'POST'])
def detail(vin, type):
    # Manager
    # 1. Basic car information
    # 2. Inventory clerk name, invoice price, and data added
    # 3. SALE SECTION salespeople name, list price, sold price, sold date,
    # and customer(individual name)(business name, contact name, title)[email, phone, street city state postal code]
    # 4. service writer REPAIR SECTION customer name or business name, writer's name, start date,
    # end date, labor charge, parts costs, and total costs
    if vin is not None and type is not None:
        cursor = mysql.connection.cursor()
        session["VIN"] = vin
        vehicle_details = []
        sale_section = []
        res_repair_details = []
        if type == 'SUV':
            cursor.execute(JJQuery.show_suv_details, [vin])
            vehicle_details = cursor.fetchone()
            cursor.execute(JJQuery.find_repair_records, [vin])
            res_repair_details = cursor.fetchall()
        elif type == 'Car':
            cursor.execute(JJQuery.show_car_details, [vin])
            vehicle_details = cursor.fetchone()
            cursor.execute(JJQuery.find_repair_records, [vin])
            res_repair_details = cursor.fetchall()
        elif type == 'Convertible':
            cursor.execute(JJQuery.show_convertible_details, [vin])
            vehicle_details = cursor.fetchone()
            cursor.execute(JJQuery.find_repair_records, [vin])
            res_repair_details = cursor.fetchall()
        elif type == 'Van':
            cursor.execute(JJQuery.show_vanminivan_details, [vin])
            vehicle_details = cursor.fetchone()
            cursor.execute(JJQuery.find_repair_records, [vin])
            res_repair_details = cursor.fetchall()
        elif type == 'Truck':
            cursor.execute(JJQuery.show_truck_details, [vin])
            vehicle_details = cursor.fetchone()
            cursor.execute(JJQuery.find_repair_records, [vin])
            res_repair_details = cursor.fetchall()
        # remove None value for unsold vehicle
        vehicle_details = [i for i in vehicle_details if i is not None]
        vehicle_details_size = len(vehicle_details)
        for index in range(vehicle_details_size - 9, vehicle_details_size - 1):
            if index == vehicle_details_size - 2:
                sale_section.append(vehicle_details[index].split(','))
            elif index == vehicle_details_size - 3:
                sale_section.append(vehicle_details[index].split(',')[1:])
            else:
                sale_section.append(vehicle_details[index])

        repair_details = []
        part_list = []
        for detail in res_repair_details:
            repair_list = []
            sub_part_list = []
            date_part_dict = dict.fromkeys(["date", "part"])
            for i in range(len(detail)):
                if i <= 7:
                    repair_list.append(detail[i])
                else:
                    sub_part_list.append(detail[i])
                    date_part_dict["date"] = detail[2]
                    date_part_dict["part"] = sub_part_list
            part_list.append(date_part_dict)
            if repair_list not in repair_details:
                repair_details.append(repair_list)

        for line in repair_details:
            total_part_cost = 0
            for part in part_list:
                if line[2] == part["date"]:
                    if part["part"][0] is not None:
                        total_part_cost += part["part"][0]
                    line.append(part["part"])
            line.append(round(total_part_cost, 2))
            line.append(round(line[7] + total_part_cost, 2))

        # ------------testing------------------
        # print("vehicle_details size", len(vehicle_details))
        # count = 0
        # for line in vehicle_details:
        #     print(count, line)
        #     count += 1
        # print()
        # print("repair detail size", len(repair_details))
        # for line in repair_details:
        #     count2 = 0
        #     print("current record's length", len(line))
        #     for value in line:
        #         print(count2, value)
        #         count2 += 1
        #     print()
        # print("sale section", len(sale_section))
        # count3 = 0
        # for line in sale_section:
        #     print(count3, line)
        #     count3 += 1
        # ------------------------------------------------
        session["last_page"] = "details"
        session["vehicle_details"] = vehicle_details
        return render_template('details.html', vehicle_details=vehicle_details,
                               sale_section=sale_section, repair_details=repair_details)
    else:
        flash("Please search first before viewing vehicle details.")
        return redirect(url_for('home'))


@app.route('/search/repair/vin=<string:vin>/type=<string:type>', methods=['GET', 'POST'])
def repairDetail(vin, type):
    # Manager
    # 1. Basic car information
    # 2. Inventory clerk name, invoice price, and data added
    # 3. SALE SECTION salespeople name, list price, sold price, sold date,
    # and customer(individual name)(business name, contact name, title)[email, phone, street city state postal code]
    # 4. service writer REPAIR SECTION customer name or business name, writer's name, start date,
    # end date, labor charge, parts costs, and total costs
    if vin is not None and type is not None:
        cursor = mysql.connection.cursor()
        session["VIN"] = vin
        session["vehicle_type"] = type
        vehicle_details = []
        sale_section = []
        repair_part_details = []
        #
        if type == 'SUV':
            cursor.execute(JJQuery.show_suv_details, [vin])
            vehicle_details = cursor.fetchone()
            cursor.execute(JJQuery.find_repair_records, [vin])
            repair_part_details = cursor.fetchall()
        elif type == 'Car':
            cursor.execute(JJQuery.show_car_details, [vin])
            vehicle_details = cursor.fetchone()
            cursor.execute(JJQuery.find_repair_records, [vin])
            repair_part_details = cursor.fetchall()
        elif type == 'Convertible':
            cursor.execute(JJQuery.show_convertible_details, [vin])
            vehicle_details = cursor.fetchone()
            cursor.execute(JJQuery.find_repair_records, [vin])
            repair_part_details = cursor.fetchall()
        elif type == 'Van':
            cursor.execute(JJQuery.show_vanminivan_details, [vin])
            vehicle_details = cursor.fetchone()
            cursor.execute(JJQuery.find_repair_records, [vin])
            repair_part_details = cursor.fetchall()
        elif type == 'Truck':
            cursor.execute(JJQuery.show_truck_details, [vin])
            vehicle_details = cursor.fetchone()
            cursor.execute(JJQuery.find_repair_records, [vin])
            repair_part_details = cursor.fetchall()
        # remove None value for unsold vehicle
        vehicle_details = [i for i in vehicle_details if i is not None]
        vehicle_details_size = len(vehicle_details)
        for index in range(vehicle_details_size - 9, vehicle_details_size - 1):
            if index == vehicle_details_size - 2:
                sale_section.append(vehicle_details[index].split(','))
            elif index == vehicle_details_size - 3:
                sale_section.append(vehicle_details[index].split(',')[1:])
            else:
                sale_section.append(vehicle_details[index])

        repair_details = []
        part_list = []
        for detail in repair_part_details:
            repair_list = []
            sub_part_list = []
            date_part_dict = dict.fromkeys(["date", "part"])
            for i in range(len(detail)):
                if i <= 7:
                    repair_list.append(detail[i])
                else:
                    sub_part_list.append(detail[i])
                    date_part_dict["date"] = detail[2]
                    date_part_dict["part"] = sub_part_list
            part_list.append(date_part_dict)
            if repair_list not in repair_details:
                repair_details.append(repair_list)

        for line in repair_details:
            total_part_cost = 0
            for part in part_list:
                if line[2] == part["date"]:
                    if part["part"][0] is not None:
                        total_part_cost += part["part"][0]
                    line.append(part["part"])
            line.append(round(total_part_cost, 2))
            line.append(round(line[7] + total_part_cost, 2))
        # store unfinished repair info
        for repair in repair_details:
            if repair[6] == 0:
                session["unfinished_repair"] = {
                    "ID": repair[0].split(',')[0],
                    "customer": repair[0].split(',')[1:],
                    "writer": repair[1],
                    "startDate": str(repair[2]),
                    "odometer": repair[4],
                    "charge": repair[7],
                    "part_cost": repair[9],
                    "total": repair[10],
                    "desc": repair[5]
                }

        cursor.execute(JJQuery.check_vehicle_part_exist, [vin])
        has_part = cursor.fetchone()
        if has_part:
            has_part = has_part[0]

        cursor.execute(JJQuery.check_unfinished_repair_exist, [vin])
        has_unfinished = cursor.fetchone()

        # remove None type in a list of list
        repair_w_part = [x for x in repair_part_details if x[8] is not None]
        # ------------testing------------------
        # print("vehicle_details size", len(vehicle_details))
        # count = 0
        # for line in vehicle_details:
        #     print(count, line)
        #     count += 1
        # print()
        # print("repair detail size", len(repair_details))
        # for line in repair_details:
        #     count2 = 0
        #     print("current record's length", len(line))
        #     for value in line:
        #         print(count2, value)
        #         count2 += 1
        # print()
        # for line in repair_part_details:
        #     print(line)
        #
        # print("part list")
        # print(part_list)
        # if repair_details[0][6] == 1:
        #     print(repair_details[0][6])
        # print("sale section", len(sale_section))
        # count3 = 0
        # for line in sale_section:
        #     print(count3, line)
        #     count3 += 1
        # ------------------------------------------------
        session["last_page"] = "add_repair"
        return render_template('repair_details.html', vehicle_details=vehicle_details, has_part=has_part,
                               has_unfinished=has_unfinished, repair_details=repair_details,
                               repair_part=repair_w_part)
    else:
        flash("Please search first before viewing vehicle details.")
        return redirect(url_for('home'))


@app.route('/addCustomer', methods=["GET", "POST"])
def addCustomer():
    # Return:
    # session['customer'] will be set which contains customer_id
    # session['VIN'] contains selected VIN number which is set from vehicle detail page
    individual_form = IndividualForm()
    business_form = BusinessForm()
    cursor = mysql.connection.cursor()

    if "role" in session:
        if request.method == 'GET' and session['role'] in ['Owner', 'Salesperson', "Service Writer"]:
            return render_template("add_customer.html", form1=individual_form, form2=business_form)

        elif request.method == 'POST':
            if individual_form.validate_on_submit():
                input_individual = dict()
                input_customer = dict()

                # for individual table
                input_individual["DLNumber"] = individual_form.DL_number.data
                input_individual["FirstName"] = individual_form.individual_first_name.data
                input_individual["LastName"] = individual_form.individual_last_name.data

                # for customer table
                input_customer["EmailAddress"] = individual_form.email.data
                input_customer["PhoneNum"] = individual_form.phone_number.data
                input_customer["StreetAdd"] = individual_form.street.data
                input_customer["City"] = individual_form.city.data
                input_customer["State"] = individual_form.state.data
                input_customer["PostalCode"] = individual_form.postal_code.data
                input_customer["Type"] = "Individual"

                cursor.execute(JJQuery.find_individual_customer, [input_individual["DLNumber"]])
                res_individual = cursor.fetchone()
                if res_individual:
                    flash("Add failed. We have this customer in our database. Do you want to search instead ?")
                    return render_template("add_customer.html", form1=individual_form, form2=business_form)
                cursor.execute(JJQuery.add_customer, input_customer)
                mysql.connection.commit()

                # ------------------------------------------
                # # reset customer auto increment
                # cursor.execute("alter table customer auto_increment = 200;")
                # mysql.connection.commit()
                # cursor.execute("alter table individual auto_increment = 167;")
                # mysql.connection.commit()
                # cursor.execute("alter table business auto_increment = 33;")
                # mysql.connection.commit()
                # -------------------------------------------
                # get last inserted customer ID
                cursor.execute("SELECT LAST_INSERT_ID();")
                last_customer_id = cursor.fetchone()
                input_individual["Customer_ID"] = last_customer_id[0]
                # print(last_customer_id[0])
                cursor.execute(JJQuery.add_individual, input_individual)
                mysql.connection.commit()

                session["customer"] = {
                    "customer_id": last_customer_id,
                    "customer_type": "Individual",
                    "customer_name": individual_form.individual_first_name.data + " " +
                                     individual_form.individual_last_name.data
                }

                if session["last_page"] == "details":
                    session["last_page"] = "add_customer"
                    return redirect(url_for("salesOrder", vin=session["VIN"]))
                elif session["last_page"] == "add_repair":
                    session["last_page"] = "add_customer"
                    return redirect(url_for("repairDetail", vin=session["VIN"], type=session["vehicle_type"]))

            elif business_form.validate_on_submit():
                input_business = dict()
                input_customer = dict()

                # for business table
                input_business["TIN"] = business_form.TIN_number.data
                input_business["BusinessName"] = business_form.business_name.data
                input_business["Contact_FirstName"] = business_form.pc_first_name.data
                input_business["Contact_LastName"] = business_form.pc_last_name.data
                input_business["ContactTitle"] = business_form.pc_title.data
                input_business["Customer_ID"] = "business_form.individual_first_name.data"

                # for customer table
                input_customer["EmailAddress"] = business_form.email.data
                input_customer["PhoneNum"] = business_form.phone_number.data
                input_customer["StreetAdd"] = business_form.street.data
                input_customer["City"] = business_form.city.data
                input_customer["State"] = business_form.state.data
                input_customer["PostalCode"] = business_form.postal_code.data
                input_customer["Type"] = "Business"

                cursor.execute(JJQuery.find_business_customer, [input_business["TIN"]])
                res_business = cursor.fetchone()
                if res_business:
                    flash("Add failed. We have this customer in our database. Do you want to search instead ?")
                    return render_template("add_customer.html", form1=individual_form, form2=business_form)
                cursor.execute(JJQuery.add_customer, input_customer)
                mysql.connection.commit()

                # ------------------------------------------
                # # reset customer auto increment
                # cursor.execute("alter table customer auto_increment = 200;")
                # mysql.connection.commit()
                # -------------------------------------------
                # get last inserted customer ID
                cursor.execute("SELECT LAST_INSERT_ID();")
                last_customer_id = cursor.fetchone()
                input_business["Customer_ID"] = last_customer_id[0]
                # print(last_customer_id[0])
                cursor.execute(JJQuery.add_business, input_business)
                mysql.connection.commit()

                session["customer"] = {
                    "customer_id": last_customer_id,
                    "customer_type": "Business",
                    "business_name": business_form.business_name.data,
                    "customer_name": business_form.pc_first_name.data + " " + business_form.pc_last_name.data
                }

                if session["last_page"] == "details":
                    session["last_page"] = "add_customer"
                    return redirect(url_for("salesOrder", vin=session["VIN"]))

                elif session["last_page"] == "add_repair":
                    session["last_page"] = "add_customer"
                    return redirect(url_for("repairDetail", vin=session["VIN"], type=session["vehicle_type"]))

            else:
                flash("Submit failed. Please submit again!")
                return redirect(url_for('home'))
        else:
            flash("You can't access this page without performing transaction.")
            return redirect(url_for('home'))
    else:
        flash("Anonymous Access is not allowed.")
        return redirect(url_for('home'))


@app.route('/searchCustomer', methods=['POST', 'GET'])
def searchCustomer():
    # Return:
    # session['customer'] will be set which contains customer_id
    # session['VIN'] contains selected VIN number which is set from vehicle detail page
    cursor = mysql.connection.cursor()

    if "role" in session:
        if request.method == "POST" and \
                session['role'] in ["Owner", "Salesperson", "Service Writer"]:
            customer_type = request.form.get("customer_type")
            customer_TIN_DL = request.form.get("customer_TIN_DL")
            if customer_type == "Individual":
                cursor.execute(JJQuery.find_individual_customer, [customer_TIN_DL])
                res_individual = cursor.fetchone()
                if res_individual:
                    session["customer"] = {
                        "customer_id": res_individual[0],
                        "customer_type": "Individual",
                        "customer_name": res_individual[2],
                        "customer_phone": res_individual[4],
                        "customer_email": res_individual[3],
                        "customer_address": res_individual[5],
                    }
                else:
                    session["customer"]["customer_id"] = None
                    flash("We don't have this customer in our Individual table. Add new customer instead ?")

            elif customer_type == "Business":
                cursor.execute(JJQuery.find_business_customer, [customer_TIN_DL])
                res_business = cursor.fetchone()
                if res_business:
                    session["customer"] = {
                        "customer_id": res_business[0],
                        "customer_type": "Business",
                        "business_name": res_business[2],
                        "customer_name": res_business[3],
                        "customer_phone": res_business[6],
                        "customer_email": res_business[5],
                        "customer_address": res_business[7],
                    }
                else:
                    session["customer"]["customer_id"] = None
                    flash("We don't have this customer in our Business table. Add new customer instead ?")
            else:
                session["customer"]["customer_id"] = None
                flash("Please choose customer type first.")

            return render_template('search_customer.html', session=session)
        else:
            session["customer"] = {
                "customer_id": None,
                "customer_type": None,
                "business_name": None,
                "customer_name": None
            }
            return render_template('search_customer.html', session=session)
    else:
        flash("Anonymous Access is not allowed.")
        return redirect(url_for("home"))


@app.route('/addVehicle', methods=['POST', 'GET'])
def addVehicle():
    add_new_vehicle_form = addNewVehicleForm()
    if request.method == 'GET':
        return render_template('register_new_vehicle.html', form=add_new_vehicle_form)
    else:
        if request.form['vehicleType'] == "Choose vehicle type":
            flash("Please choose a vehicle type")
            return render_template('register_new_vehicle.html', form=add_new_vehicle_form)
        parameters = {
            "vin": request.form['vin'],
            "manufacturer": request.form['manufacturer'],
            "modelName": request.form['modelName'],
            "modelYear": int(request.form['modelYear']),
            "vehicleType": request.form['vehicleType'],
            "colors": request.form.getlist('colors'),
            "description": request.form['description'],
            "dateAdded": datetime.now().date(),
            "userName": session['username']
        }

        if isinstance(add_new_vehicle_form.invoicePrice.data, numbers.Number):
            parameters["invoicePrice"] = float(round(add_new_vehicle_form.invoicePrice.data, 2))
        else:
            flash("Please Enter a valid integer for invoice price.")
            return render_template('register_new_vehicle.html', form=add_new_vehicle_form)

        if request.form['numberOfDoors'].isdigit():
            parameters["numberOfDoors"] = int(request.form['numberOfDoors'])
        else:
            flash("Please Enter a valid integer for number of doors.")
            return render_template('register_new_vehicle.html', form=add_new_vehicle_form)

        if isinstance(add_new_vehicle_form.cargoCapacity.data, numbers.Number):
            parameters["cargoCapacity"] = float(request.form['cargoCapacity'])
        else:
            flash("Please Enter a valid integer for cargo capacity.")
            return render_template('register_new_vehicle.html', form=add_new_vehicle_form)

        if isinstance(request.form['cargoCoverType'], str):
            parameters["cargoCoverType"] = request.form['cargoCoverType']
        else:
            flash("Please Enter a valid integer for cargo cover type.")
            return render_template('register_new_vehicle.html', form=add_new_vehicle_form)

        if request.form['noOfRearAxles'].isdigit():
            parameters["noOfRearAxles"] = int(request.form['noOfRearAxles'])
        else:
            flash("Please Enter a valid integer for number of rear axles.")
            return render_template('register_new_vehicle.html', form=add_new_vehicle_form)

        if isinstance(request.form['drivetrainType'], str):
            parameters["drivetrainType"] = request.form['drivetrainType']
        else:
            flash("Please Enter a valid integer for drivetrain type.")
            return render_template('register_new_vehicle.html', form=add_new_vehicle_form)

        if request.form['noOfCupHolders'].isdigit():
            parameters["noOfCupHolders"] = int(request.form['noOfCupHolders'])
        else:
            flash("Please Enter a valid integer for number of cup holder.")
            return render_template('register_new_vehicle.html', form=add_new_vehicle_form)

        if isinstance(request.form['roofType'], str):
            parameters["roofType"] = request.form['roofType']
        else:
            flash("Please Enter a valid integer for roof type.")
            return render_template('register_new_vehicle.html', form=add_new_vehicle_form)

        if request.form['backSeatCount'].isdigit():
            parameters["backSeatCount"] = int(request.form['backSeatCount'])
        else:
            flash("Please Enter a valid integer for back seat count.")
            return render_template('register_new_vehicle.html', form=add_new_vehicle_form)

        if request.form['hasBackDoor']:
            parameters["hasBackDoor"] = int(request.form['hasBackDoor'])

        cursor = mysql.connection.cursor()

        cursor.execute(JJQuery.get_vehicles_by_vin, [parameters["vin"]])
        does_vehicle_exists = cursor.fetchone() is not None

        if not does_vehicle_exists:
            cursor.execute(JJQuery.get_manufacture, [parameters["manufacturer"]])
            does_manufacture_exists = cursor.fetchone() is not None
            if not does_manufacture_exists:
                cursor.execute(JJQuery.add_a_manufacture, [parameters["manufacturer"]])

            cursor.execute(JJQuery.add_a_vehicle, parameters)

            if parameters["vehicleType"] == "Car":
                cursor.execute(JJQuery.add_a_car, parameters)
            elif parameters["vehicleType"] == "SUV":
                cursor.execute(JJQuery.add_a_suv, parameters)
            elif parameters["vehicleType"] == "Truck":
                cursor.execute(JJQuery.add_a_truck, parameters)
            elif parameters["vehicleType"] == "Van":
                cursor.execute(JJQuery.add_a_van, parameters)
            elif parameters["vehicleType"] == "Convertible":
                cursor.execute(JJQuery.add_a_convertible, parameters)

            for color in parameters["colors"]:
                cursor.execute(JJQuery.add_vehicle_color, [parameters["vin"], color])

            mysql.connection.commit()
            cursor.close()
            return redirect(url_for("detail", vin=parameters["vin"], type=parameters["vehicleType"]))
        else:
            flash("This vehicle already exists!")
            return render_template('register_new_vehicle.html', form=add_new_vehicle_form)


@app.route('/salesOrder', methods=['GET', 'POST'])
def salesOrder():
    form = salesOrderForm()
    if request.method == 'GET':
        if session["last_page"] in ["home", "search"]:
            session.pop("customer", None)
        session["last_page"] = "salesOrder"
        return render_template('salesOrder.html', vehicle_details=session["vehicle_details"], form=form)
    if request.method == 'POST':
        if isinstance(form.price.data, numbers.Number):
            price = float(request.form["price"])
        else:
            flash("Please enter a valid price format")
            return render_template('salesOrder.html', vehicle_details=session["vehicle_details"], form=form)
        type = session["vehicle_details"][1]
        use_fk_dictionary_next_time = 0.0
        if type == "Convertible" or type == "SUV":
            use_fk_dictionary_next_time = session["vehicle_details"][10]
        elif type == "Car" or type == "Van":
            use_fk_dictionary_next_time = session["vehicle_details"][9]
        elif type == "Truck":
            use_fk_dictionary_next_time = session["vehicle_details"][11]

        if price <= use_fk_dictionary_next_time * 0.95 and session["role"] != "Owner":
            flash("Sale Price Too Low!")
            return render_template('salesOrder.html', vehicle_details=session["vehicle_details"], form=form)

        cursor = mysql.connection.cursor()
        cursor.execute(JJQuery.add_a_sale, [session["vehicle_details"][0], session["username"],
                                            session["customer"]["customer_id"], request.form["purchaseDate"],
                                            price])
        mysql.connection.commit()
        return redirect(url_for("detail", vin=session["vehicle_details"][0], type=session["vehicle_details"][1]))


@app.route('/repair', methods=['GET', 'POST'])
def repair():
    search_by_vin_form = searchByVinForm()
    cursor = mysql.connection.cursor()
    if "role" in session:
        if request.method == 'GET' and session['role'] in ['Owner', "Service Writer"]:
            ## get sold vehicles with no repair records
            # Query = "SELECT sale.VIN FROM sale left join repair on sale.VIN = repair.vin where repair.vin is null;"
            # # get repair vehicles with no part records
            # Query = "SELECT repair.VIN FROM repair left join part on " \
            #         "repair.VIN = part.vin " \
            #         "where part.vin is null;"
            # cursor.execute(Query)
            # res = cursor.fetchall()
            # print("# of 0 repair vehicles", len(res))
            # for line in res:
            #     print(line)
            return render_template("repair.html", form=search_by_vin_form)
        else:
            flash("Only Owner and Service Writer can access repair section.")
            return redirect(url_for('home'))
    else:
        flash("Anonymous Access is not allowed.")
        return redirect(url_for('home'))


@app.route('/addRepair', methods=['GET', 'POST'])
def addRepair():
    cursor = mysql.connection.cursor()
    if "role" in session:
        if session['role'] in ['Owner', "Service Writer"]:
            if request.method == 'GET':
                flash("Please Search your vehicle first before operating repairs.")
                return redirect(url_for("repair"))

            elif request.method == 'POST':
                if "addRepair" in request.form:
                    if session["customer"] is None:
                        flash("Please search customer first.")
                    else:
                        new_repair = dict()
                        new_repair["VIN"] = session["VIN"]
                        # new_repair["startDate"] = request.form.get("date")
                        new_repair["startDate"] = session["dateNow"]
                        new_repair["customerID"] = session["customer"]["customer_id"]
                        new_repair["desc"] = request.form.get("desc")
                        new_repair["charge"] = request.form.get("charge")
                        new_repair["odometer"] = request.form.get("odometer")
                        new_repair["username"] = session['username']

                        cursor.execute(JJQuery.check_new_repair_valid, [new_repair["VIN"], new_repair["startDate"]])
                        res_check_new_repair = cursor.fetchone()
                        if res_check_new_repair:
                            flash("It is not allowed to create repair ticket on the same day!")
                        else:
                            cursor.execute(JJQuery.insert_repair, new_repair)
                            mysql.connection.commit()
                elif "updateCharge" in request.form:
                    new_charge = float(request.form.get("charge"))
                    previous_charge = session["unfinished_repair"]["charge"]
                    if new_charge < previous_charge:
                        if session['role'] == "Service Writer":
                            flash("New Labor charge cannot be less than previous value: {}. ".format(previous_charge))
                            return redirect(url_for("repairDetail", vin=session["VIN"], type=session["vehicle_type"]))
                    update_charge = {
                        "charge": new_charge,
                        "VIN": session["VIN"],
                        "startDate": session["unfinished_repair"]["startDate"]
                    }
                    cursor.execute(JJQuery.update_labor_charge, update_charge)
                    mysql.connection.commit()
                return redirect(url_for("repairDetail", vin=session["VIN"], type=session["vehicle_type"]))
        else:
            flash("Only Owner and Service Writer can access repair section.")
            return redirect(url_for('home'))
    else:
        flash("Anonymous Access is not allowed.")
        return redirect(url_for('home'))


@app.route('/addPart', methods=['GET', 'POST'])
def addPart():
    cursor = mysql.connection.cursor()
    if "role" in session:
        if session['role'] in ['Owner', "Service Writer"]:
            if request.method == 'GET':
                flash("Please Search your vehicle first before operating repairs.")
                return redirect(url_for("repair"))

            elif request.method == 'POST':
                if "addPart" in request.form:
                    new_part = dict()
                    new_part["VIN"] = session["VIN"]
                    new_part["startDate"] = session["unfinished_repair"]["startDate"]
                    new_part["customerID"] = session["unfinished_repair"]["ID"]
                    new_part["part_number"] = request.form.get("part_number")
                    new_part["vendor_name"] = request.form.get("vendor_name")
                    new_part["quantity"] = request.form.get("quantity")
                    new_part["price"] = request.form.get("price")
                    cursor.execute(JJQuery.check_new_part_valid, [new_part["VIN"],
                                                                  new_part["startDate"], new_part["part_number"]])
                    res_check_new_repair = cursor.fetchone()
                    if res_check_new_repair:
                        flash("You can't enter duplicate part number for current repair!")
                    else:
                        cursor.execute(JJQuery.insert_part, new_part)
                        mysql.connection.commit()
                    return redirect(url_for("repairDetail", vin=session["VIN"], type=session["vehicle_type"]))
        else:
            flash("Only Owner and Service Writer can access repair section.")
            return redirect(url_for('home'))
    else:
        flash("Anonymous Access is not allowed.")
        return redirect(url_for('home'))


@app.route('/completeRepair', methods=['GET', 'POST'])
def completeRepair():
    cursor = mysql.connection.cursor()
    if "role" in session:
        if session['role'] in ['Owner', "Service Writer"]:
            if request.method == 'GET':
                flash("Please Search your vehicle first before operating repairs.")
                return redirect(url_for("repair"))
            if request.method == "POST":
                # endDate = request.form.get("endDate")
                endDate = session["dateNow"]
                VIN = session["VIN"]
                startDate = session["unfinished_repair"]["startDate"]
                cursor.execute(JJQuery.complete_repair, [endDate, VIN, startDate])
                mysql.connection.commit()
                return redirect(url_for("repairDetail", vin=session["VIN"], type=session["vehicle_type"]))
            else:
                return redirect(url_for("repairDetail", vin=session["VIN"], type=session["vehicle_type"]))
        else:
            flash("Only Owner and Service Writer can access repair section.")
            return redirect(url_for('home'))
    else:
        flash("Anonymous Access is not allowed.")
        return redirect(url_for('home'))


@app.route('/reports', methods=['POST'])
def reports():
    report_request = request.form['reports']
    if "get_SalesbyColor" in report_request:
        return redirect(url_for("get_SalesbyColor"))
    elif "get_SalesbyType" in report_request:
        return redirect(url_for("get_SalesbyType"))
    elif "get_SalesbyManufacturer" in report_request:
        return redirect(url_for("get_SalesbyManufacturer"))
    elif "get_GrossCustomerIncome" in report_request:
        return redirect(url_for("get_GrossCustomerIncome"))
    elif "get_RepairsbyManufactureTypeModel" in report_request:
        return redirect(url_for("get_RepairsbyManufactureTypeModel"))
    elif "get_BelowCostSales" in report_request:
        return redirect(url_for("get_BelowCostSales"))
    elif "get_AverageTimeinInventory" in report_request:
        return redirect(url_for("get_AverageTimeinInventory"))
    elif "get_PartsStatistics" in report_request:
        return redirect(url_for("get_PartsStatistics"))
    elif "get_MonthlySales" in report_request:
        return redirect(url_for("get_MonthlySales"))
    else:
        return redirect(url_for("home"))


@app.route('/report', methods=['GET', 'POST'])
def report():
    return render_template('viewreport.html')


@app.route('/report/SalesbyColor', methods=['GET'])
def get_SalesbyColor():
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.Sale_by_color)
    data = cursor.fetchall()
    print(data)
    return render_template("display_Sale_By_Color.html", data=data)


@app.route('/report/SalesbyType', methods=['GET'])
def get_SalesbyType():
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.Sale_by_type)
    data = cursor.fetchall()
    print(data)
    return render_template("display_Sale_By_Type.html", data=data)


@app.route('/report/SalesbyManufacturer', methods=['GET'])
def get_SalesbyManufacturer():
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.Sale_by_manufacturer)
    data = cursor.fetchall()
    print(data)
    return render_template("display_Sale_By_Manufacturer.html", data=data)


@app.route('/report/belowcostsales', methods=['GET'])
def get_BelowCostSales():
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.below_cost_sales)
    data = cursor.fetchall()
    return render_template("display_below_cost_sales.html", data=data)


@app.route('/report/AverageTimeinInventory', methods=['GET'])
def get_AverageTimeinInventory():
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.average_time_inventory)
    data = cursor.fetchall()
    return render_template("display_average_time_in_inventory.html", data=data)


@app.route('/report/partstatistics', methods=['GET'])
def get_PartsStatistics():
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.part_statistics)
    data = cursor.fetchall()
    return render_template("display_part_statistics.html", data=data)


@app.route('/report/monthlysales', methods=['GET'])
def get_MonthlySales():
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.monthly_sales_summary)
    data = cursor.fetchall()
    return render_template("display_monthly_sales_summary.html", data=data)


@app.route('/report/monthlysales/Yearmonth=<string:Yearmonth>', methods=['GET'])
def get_MonthlySalesDrilldown(Yearmonth=''):
    print(Yearmonth)
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.monthly_sales_drilldown, [Yearmonth])
    salesperson = cursor.fetchall()
    return render_template("display_monthly_sales_drilldown.html", salesperson=salesperson, text=Yearmonth)


@app.route('/report/grosscustomerincome', methods=['GET'])
def get_GrossCustomerIncome():
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.gross_customer_income)
    data = cursor.fetchall()
    return render_template("display_gross_customer_income.html", data=data[:15])


@app.route('/report/grosscustomerincomedrilldown/Customer_ID=<string:Customer_ID>', methods=['GET'])
def get_GrossCustomerIncomeDrilldown(Customer_ID=''):
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.gross_customer_income_salerecords, [Customer_ID])
    datasale = cursor.fetchall()
    cursor.execute(JJQuery.gross_customer_income_repairrecords, [Customer_ID])
    datarepair = cursor.fetchall()
    return render_template("display_gross_customer_income_drilldown.html", datasale=datasale, datarepair=datarepair)


@app.route('/report/repairbymanufacturer', methods=['GET'])
def get_RepairsbyManufactureTypeModel():
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.repair_by_manufacturer)
    data = cursor.fetchall()
    return render_template("display_repair_by_manufacturer.html", data=data)


@app.route('/report/repairbymanufacturerdrilldown/ManufacturerName=<string:ManufacturerName>', methods=['GET'])
def get_RepairsbyManufactureDrilldown(ManufacturerName=''):
    # print(ManufacturerName)
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.repair_by_type, [ManufacturerName])
    datavehicletype = cursor.fetchall()
    return render_template("display_repair_by_manufacturer_drilldown.html", datavehicletype=datavehicletype,
                           text=ManufacturerName)


@app.route(
    '/report/repairbymanufacturertypedrilldown/ManufacturerName=<string:ManufacturerName>/VehicleType=<string:VehicleType>',
    methods=['GET'])
def get_RepairsbyManufactureTypeDrilldown(ManufacturerName='', VehicleType=''):
    # print(ManufacturerName, VehicleType)
    cursor = mysql.connection.cursor()
    cursor.execute(JJQuery.repair_by_model, [ManufacturerName, VehicleType])
    datavehiclemodel = cursor.fetchall()
    # print(len(datavehiclemodel))
    return render_template("display_repair_by_manufacturer_type_drilldown.html", datavehiclemodel=datavehiclemodel,
                           text=[ManufacturerName, VehicleType])


if __name__ == '__main__':
    app.run(debug=True)
