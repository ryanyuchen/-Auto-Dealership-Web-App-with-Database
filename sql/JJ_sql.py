class JJQuery:
    #constructor
    def __init__(self):
        pass

    @property
    def validate_user(self):
        return """SELECT Password FROM loggedinuser WHERE loggedinuser.Username = %s"""

    @property
    def find_user_role(self):
        return """
            SELECT loggedinuser.Username, loggedinuser.Password,
            CASE WHEN loggedinuser.Username = owner.Username THEN 'Owner'
            WHEN loggedinuser.Username = manager.Username THEN 'Manager'
            WHEN loggedinuser.Username = servicewriter.Username THEN 'Service Writer'
            WHEN loggedinuser.Username = inventoryclerk.Username THEN 'Inventory Clerk'
            WHEN loggedinuser.Username = salesperson.Username THEN 'Salesperson'
            END AS Role
            FROM loggedinuser
            LEFT JOIN owner
             ON loggedinuser.Username = owner.Username
            LEFT JOIN manager
             ON loggedinuser.Username = manager.Username
            LEFT JOIN servicewriter
             ON loggedinuser.Username = servicewriter.Username
            LEFT JOIN inventoryclerk
             ON loggedinuser.Username = inventoryclerk.Username
            LEFT JOIN salesperson
             ON loggedinuser.Username = salesperson.Username
            WHERE loggedinuser.Username = %s"""

    @property
    def count_number_of_vehicles(self):
        return """SELECT COUNT(vehicle.VIN)
            FROM vehicle
            LEFT JOIN
            (SELECT DISTINCT(VIN) AS DistinctVIN FROM repair)
            as vehicles_in_repair
            ON vehicle.VIN = vehicles_in_repair.DistinctVIN
            LEFT JOIN sale
            ON vehicle.VIN = sale.VIN
            WHERE vehicles_in_repair.DistinctVIN IS NULL AND sale.VIN IS NULL"""

    @property
    def get_manufacturer_name(self):
        return """SELECT manufacturer.ManufacturerName from manufacturer;"""

    @property
    def get_colors(self):
        return """SELECT DISTINCT Color from vehiclecolor;"""

    @property
    def get_selected_unsold_vehicles(self):
        return """SELECT vehicle.VIN, vehicles_with_types.VehicleType, vehicle.ModelYear,
            vehicle.ManufacturerName, vehicle.ModelName, vehicles_with_colors_grouped.Color,
            vehicle.OptionalDescription as Description, ROUND(vehicle.InvoicePrice*1.2, 2) as ListPrice,
            CASE
            WHEN vehicle.OptionalDescription LIKE %(res_keyword)s THEN 'Yes'
            ELSE 'No'
            END AS DesMatch
            FROM vehicle
            LEFT JOIN
            (
            SELECT suv.VIN, "SUV" as VehicleType FROM suv
            UNION ALL
            SELECT truck.VIN, "Truck" as VehicleType FROM truck
            UNION ALL
            SELECT vanminivan.VIN, "Van" as VehicleType FROM vanminivan
            UNION ALL
            SELECT car.VIN, "Car" as VehicleType FROM car
            UNION ALL
            SELECT convertible.VIN, "Convertible" as VehicleType FROM convertible
            ) as vehicles_with_types
            ON vehicles_with_types.VIN = vehicle.VIN
            LEFT JOIN
            (
            SELECT vehiclecolor.VIN, GROUP_CONCAT(vehiclecolor.Color
            ORDER BY Color ASC) as Color
            FROM vehiclecolor
            GROUP BY VIN
            ) as vehicles_with_colors_grouped
            ON vehicles_with_colors_grouped.VIN = vehicle.VIN
            LEFT JOIN sale
            ON vehicle.VIN = sale.VIN
            WHERE
            sale.VIN IS NULL
            AND
            (ManufacturerName = %(res_manufacturer)s OR %(res_manufacturer)s = 'All Manufacturers' OR %(res_manufacturer)s IS NULL)
            AND
            (VehicleType = %(res_type)s OR %(res_type)s = 'All Vehicle Types' OR %(res_type)s IS NULL)
            AND
            (ModelYear = %(res_year)s OR %(res_year)s = 'All Model Years' OR %(res_year)s IS NULL)
            AND
            (Color = %(res_color)s OR %(res_color)s = 'All Colors' OR %(res_color)s IS NULL)
            AND
            (InvoicePrice*1.2 < %(res_price_range)s OR %(res_price_range)s = 'Range' OR %(res_price_range)s IS NULL)
            AND
            (ManufacturerName LIKE %(res_keyword)s OR
            ModelName LIKE %(res_keyword)s OR
            ModelYear LIKE %(res_keyword)s OR
            OptionalDescription LIKE %(res_keyword)s)
            ORDER BY vehicle.VIN;"""

    @property
    def get_vehicles_by_vin(self):
        return """SELECT vehicle.VIN, vehicles_with_types.VehicleType, vehicle.ModelYear,
               vehicle.ManufacturerName, vehicle.ModelName, vehicles_with_colors_grouped.Color,
               vehicle.OptionalDescription as Description, ROUND(vehicle.InvoicePrice*1.2, 2) as ListPrice,
               CASE WHEN sale.VIN IS NOT NULL THEN "Sold" ELSE "Unsold"
               END AS sale_status
               FROM vehicle
               LEFT JOIN
               (
               SELECT suv.VIN, "SUV" as VehicleType FROM suv
               UNION ALL
               SELECT truck.VIN, "Truck" as VehicleType FROM truck
               UNION ALL
               SELECT vanminivan.VIN, "Van" as VehicleType FROM vanminivan
               UNION ALL
               SELECT car.VIN, "Car" as VehicleType FROM car
               UNION ALL
               SELECT convertible.VIN, "Convertible" as VehicleType FROM convertible
               ) as vehicles_with_types
               ON vehicles_with_types.VIN = vehicle.VIN
               LEFT JOIN
               (
               SELECT vehiclecolor.VIN, GROUP_CONCAT(vehiclecolor.Color
               ORDER BY Color ASC) as Color
               FROM vehiclecolor
               GROUP BY VIN
               ) as vehicles_with_colors_grouped
               ON vehicles_with_colors_grouped.VIN = vehicle.VIN
               LEFT JOIN sale
               ON vehicle.VIN = sale.VIN
               WHERE vehicle.VIN = %s;"""

    @property
    def get_vehicles_by_filter(self):
        return """SELECT vehicle.VIN, vehicles_with_types.VehicleType, vehicle.ModelYear,
               vehicle.ManufacturerName, vehicle.ModelName, vehicles_with_colors_grouped.Color,
               vehicle.OptionalDescription as Description, ROUND(vehicle.InvoicePrice*1.2, 2) as ListPrice
               FROM vehicle
               LEFT JOIN
               (
               SELECT suv.VIN, "SUV" as VehicleType FROM suv
               UNION ALL
               SELECT truck.VIN, "Truck" as VehicleType FROM truck
               UNION ALL
               SELECT vanminivan.VIN, "Van" as VehicleType FROM vanminivan
               UNION ALL
               SELECT car.VIN, "Car" as VehicleType FROM car
               UNION ALL
               SELECT convertible.VIN, "Convertible" as VehicleType FROM convertible
               ) as vehicles_with_types
               ON vehicles_with_types.VIN = vehicle.VIN
               LEFT JOIN
               (
               SELECT vehiclecolor.VIN, GROUP_CONCAT(vehiclecolor.Color
               ORDER BY Color ASC) as Color
               FROM vehiclecolor
               GROUP BY VIN
               ) as vehicles_with_colors_grouped
               ON vehicles_with_colors_grouped.VIN = vehicle.VIN
               LEFT JOIN sale
               ON vehicle.VIN = sale.VIN
               WHERE CASE
               WHEN %(filter)s = "All Vehicles" THEN vehicle.VIN IS NOT NULL
               WHEN %(filter)s = "Sold Vehicles" THEN sale.VIN IS NOT NULL
               WHEN %(filter)s = "Unsold Vehicles" THEN sale.VIN IS NULL
               END;"""

    @property
    def add_customer(self):
        return """INSERT INTO customer (EmailAddress, PhoneNum, StreetAdd, City, State, PostalCode)
        VALUES(%(EmailAddress)s, %(PhoneNum)s, %(StreetAdd)s, %(City)s, %(State)s, %(PostalCode)s);"""

    @property
    def add_individual(self):
        return """INSERT INTO individual (DLNumber, FirstName, LastName, Customer_ID)
        VALUES(%(DLNumber)s, %(FirstName)s, %(LastName)s, %(Customer_ID)s);"""

    @property
    def add_business(self):
        return """INSERT INTO business (TIN, BusinessName, Contact_FirstName, Contact_LastName, ContactTitle, Customer_ID)
        VALUES(%(TIN)s, %(BusinessName)s, %(Contact_FirstName)s, %(Contact_LastName)s, %(ContactTitle)s, %(Customer_ID)s);"""


    @property
    def find_individual_customer(self):
        return """SELECT
            individual.Customer_ID,
            individual.DLNumber,
            CONCAT_WS(' ', individual.FirstName, individual.LastName),
            customer.EmailAddress,
            customer.PhoneNum,
            CONCAT_WS(', ', customer.StreetAdd, customer.City, customer.State, customer.PostalCode),
            customer.StreetAdd,
            customer.City,
            Customer.State,
            Customer.PostalCode
            FROM individual
            INNER JOIN customer
            ON individual.Customer_ID = customer.Customer_ID
            WHERE
            individual.DLNumber = %s;
            """


    @property
    def find_business_customer(self):
        return """SELECT
            business.Customer_ID,
            business.TIN,
            business.BusinessName,
            CONCAT_WS(' ', business.Contact_FirstName, business.Contact_LastName),
            business.ContactTitle,
            customer.EmailAddress,
            customer.PhoneNum,
            CONCAT_WS(', ', customer.StreetAdd, customer.City, customer.State, customer.PostalCode),
            customer.StreetAdd,
            customer.City,
            customer.State,
            customer.PostalCode
            FROM business
            INNER JOIN customer
            ON business.Customer_ID = customer.Customer_ID
            WHERE
            business.TIN = %s; """


    @property
    def show_suv_details(self):
        return """SELECT vehicle.VIN, "SUV" AS type, vehicle.ModelYear,
            vehicle.ModelName, vehicle.ManufacturerName, vehicles_with_colors_grouped.Color,
            ROUND(vehicle.InvoicePrice*1.2, 2) as ListPrice, vehicle.OptionalDescription as Description,
            suv.DrivetrainType, suv.NoOfCupholders,
            vehicle.InvoicePrice, vehicle.DateAdded, CONCAT_WS(' ', loggedinuser.FirstName, loggedinuser.LastName),
            sale_section.SoldPrice, sale_section.PurchaseDate, CONCAT_WS(' ', sale_section.FirstName, sale_section.LastName),
            sale_section.customerTypeInfo, sale_section.customerInfo,
            CASE WHEN sale_section.VIN IS NULL
            THEN 'Unsold'
            ELSE 'Sold'
            END AS Sale_Condition
            FROM vehicle
            LEFT JOIN suv
            ON suv.VIN = vehicle.VIN
            LEFT JOIN
            (
             SELECT vehiclecolor.VIN, GROUP_CONCAT(vehiclecolor.Color
             ORDER BY Color ASC) as Color
             FROM vehiclecolor
             GROUP BY VIN
            ) as vehicles_with_colors_grouped
            ON vehicles_with_colors_grouped.VIN = vehicle.VIN
            LEFT JOIN (
            SELECT sale.VIN, loggedinuser.FirstName, loggedinuser.LastName, sale.PurchaseDate, sale.SoldPrice,
            CASE WHEN individual.Customer_ID IS NOT NULL
            THEN ( SELECT CONCAT_WS(',', individual.Customer_ID, individual.FirstName, individual.LastName) AS IndividualInfo
            FROM individual WHERE sale.Customer_ID = individual.Customer_ID)
            ELSE (SELECT CONCAT_WS(',', business.Customer_ID, business.BusinessName, business.ContactTitle, business.Contact_FirstName,
            business.Contact_LastName) AS BusinessInfo FROM business WHERE sale.Customer_ID = business.Customer_ID)
            END AS customerTypeInfo, CONCAT_WS(',', customer.EmailAddress, customer.PhoneNum, customer.StreetAdd,
            customer.City, customer.State, customer.PostalCode) AS customerInfo
            FROM sale
            LEFT JOIN loggedinuser ON
             sale.Username = loggedinuser.Username
            LEFT JOIN customer ON
             customer.Customer_ID = sale.Customer_ID
            LEFT JOIN individual ON
             sale.Customer_ID = individual.Customer_ID
            LEFT JOIN business ON
             sale.Customer_ID = business.Customer_ID
            ) as sale_section
            ON vehicle.VIN = sale_section.VIN
            LEFT JOIN loggedinuser
            ON vehicle.Username = loggedinuser.Username
            WHERE
             vehicle.VIN = %s
             ;"""


    @property
    def show_car_details(self):
        return """SELECT vehicle.VIN, "Car" AS type, vehicle.ModelYear,
            vehicle.ModelName, vehicle.ManufacturerName, vehicles_with_colors_grouped.Color,
            ROUND(vehicle.InvoicePrice*1.2, 2) as ListPrice, vehicle.OptionalDescription, car.NoOfDoors,
            vehicle.InvoicePrice, vehicle.DateAdded, CONCAT_WS(' ', loggedinuser.FirstName, loggedinuser.LastName),
            sale_section.SoldPrice, sale_section.PurchaseDate, CONCAT_WS(' ', sale_section.FirstName, sale_section.LastName),
            sale_section.customerTypeInfo, sale_section.customerInfo,
            CASE WHEN sale_section.VIN IS NULL
            THEN 'Unsold' ELSE 'Sold'
            END AS Sale_Condition
            FROM vehicle
            LEFT JOIN car
            ON car.VIN = vehicle.VIN
            LEFT JOIN
            (
            SELECT vehiclecolor.VIN, GROUP_CONCAT(vehiclecolor.Color
            ORDER BY Color ASC) as Color
            FROM vehiclecolor
            GROUP BY VIN
            ) as vehicles_with_colors_grouped
            ON vehicles_with_colors_grouped.VIN = vehicle.VIN
            LEFT JOIN (
            SELECT sale.VIN, loggedinuser.FirstName, loggedinuser.LastName, sale.PurchaseDate, sale.SoldPrice,
            CASE WHEN individual.Customer_ID IS NOT NULL
            THEN ( SELECT CONCAT_WS(',', individual.Customer_ID, individual.FirstName, individual.LastName) AS IndividualInfo
            FROM individual WHERE sale.Customer_ID = individual.Customer_ID)
            ELSE (SELECT CONCAT_WS(',', business.Customer_ID, business.BusinessName, business.ContactTitle, business.Contact_FirstName,
            business.Contact_LastName) AS BusinessInfo FROM business WHERE sale.Customer_ID = business.Customer_ID)
            END AS customerTypeInfo, CONCAT_WS(',', customer.EmailAddress, customer.PhoneNum, customer.StreetAdd,
            customer.City, customer.State, customer.PostalCode) AS customerInfo
            FROM sale
            LEFT JOIN loggedinuser ON
             sale.Username = loggedinuser.Username
            LEFT JOIN customer ON
             customer.Customer_ID = sale.Customer_ID
            LEFT JOIN individual ON
             sale.Customer_ID = individual.Customer_ID
            LEFT JOIN business ON
             sale.Customer_ID = business.Customer_ID
            ) as sale_section
            ON vehicle.VIN = sale_section.VIN
            LEFT JOIN loggedinuser
            ON vehicle.Username = loggedinuser.Username
            WHERE
            vehicle.VIN = %s;"""

    @property
    def show_truck_details(self):
        return """SELECT vehicle.VIN, "Truck" AS type, vehicle.ModelYear,
            vehicle.ModelName, vehicle.ManufacturerName, vehicles_with_colors_grouped.Color,
            ROUND(vehicle.InvoicePrice*1.2, 2) as ListPrice, vehicle.OptionalDescription as Description,
            truck.CargoCapacity, truck.CargoCoverType, truck.NoOfRearAxies,
            vehicle.InvoicePrice, vehicle.DateAdded, CONCAT_WS(' ', loggedinuser.FirstName, loggedinuser.LastName),
            sale_section.SoldPrice, sale_section.PurchaseDate, CONCAT_WS(' ', sale_section.FirstName, sale_section.LastName),
            sale_section.customerTypeInfo, sale_section.customerInfo,
            CASE WHEN sale_section.VIN IS NULL
            THEN 'Unsold' ELSE 'Sold'
            END AS Sale_Condition
            FROM vehicle
            LEFT JOIN truck
            ON truck.VIN = vehicle.VIN
            LEFT JOIN
            (
            SELECT vehiclecolor.VIN, GROUP_CONCAT(vehiclecolor.Color
            ORDER BY Color ASC) as Color
            FROM vehiclecolor
            GROUP BY VIN
            ) as vehicles_with_colors_grouped
            ON vehicles_with_colors_grouped.VIN = vehicle.VIN
            LEFT JOIN (
            SELECT sale.VIN, loggedinuser.FirstName, loggedinuser.LastName, sale.PurchaseDate, sale.SoldPrice,
            CASE WHEN individual.Customer_ID IS NOT NULL
            THEN ( SELECT CONCAT_WS(',', individual.Customer_ID, individual.FirstName, individual.LastName) AS IndividualInfo
            FROM individual WHERE sale.Customer_ID = individual.Customer_ID)
            ELSE (SELECT CONCAT_WS(',', business.Customer_ID, business.BusinessName, business.ContactTitle, business.Contact_FirstName,
            business.Contact_LastName) AS BusinessInfo FROM business WHERE sale.Customer_ID = business.Customer_ID)
            END AS customerTypeInfo, CONCAT_WS(',', customer.EmailAddress, customer.PhoneNum, customer.StreetAdd,
            customer.City, customer.State, customer.PostalCode) AS customerInfo
            FROM sale
            LEFT JOIN loggedinuser ON
             sale.Username = loggedinuser.Username
            LEFT JOIN customer ON
             customer.Customer_ID = sale.Customer_ID
            LEFT JOIN individual ON
             sale.Customer_ID = individual.Customer_ID
            LEFT JOIN business ON
             sale.Customer_ID = business.Customer_ID
            ) as sale_section
            ON vehicle.VIN = sale_section.VIN
            LEFT JOIN loggedinuser
            ON vehicle.Username = loggedinuser.Username
            WHERE
            vehicle.VIN = %s;"""

    @property
    def show_vanminivan_details(self):
        return """SELECT vehicle.VIN, "Van" AS type, vehicle.ModelYear,
            vehicle.ModelName, vehicle.ManufacturerName, vehicles_with_colors_grouped.Color,
            ROUND(vehicle.InvoicePrice*1.2, 2) AS ListPrice, vehicle.OptionalDescription as Description,
            vanMinivan.HasDriversSideBackDoor,
            vehicle.InvoicePrice, vehicle.DateAdded, CONCAT_WS(' ', loggedinuser.FirstName, loggedinuser.LastName),
            sale_section.SoldPrice, sale_section.PurchaseDate, CONCAT_WS(' ', sale_section.FirstName, sale_section.LastName),
            sale_section.customerTypeInfo, sale_section.customerInfo,
            CASE WHEN sale_section.VIN IS NULL
            THEN 'Unsold' ELSE 'Sold'
            END AS Sale_Condition
            FROM vehicle
            LEFT JOIN vanminivan
            ON vanminivan.VIN = vehicle.VIN
            LEFT JOIN
            (
            SELECT vehiclecolor.VIN, GROUP_CONCAT(vehiclecolor.Color
            ORDER BY Color ASC) as Color
            FROM vehiclecolor
            GROUP BY VIN
            ) as vehicles_with_colors_grouped
            ON vehicles_with_colors_grouped.VIN = vehicle.VIN
            LEFT JOIN (
            SELECT sale.VIN, loggedinuser.FirstName, loggedinuser.LastName, sale.PurchaseDate, sale.SoldPrice,
            CASE WHEN individual.Customer_ID IS NOT NULL
            THEN ( SELECT CONCAT_WS(',', individual.Customer_ID, individual.FirstName, individual.LastName) AS IndividualInfo
            FROM individual WHERE sale.Customer_ID = individual.Customer_ID)
            ELSE (SELECT CONCAT_WS(',', business.Customer_ID, business.BusinessName, business.ContactTitle, business.Contact_FirstName,
            business.Contact_LastName) AS BusinessInfo FROM business WHERE sale.Customer_ID = business.Customer_ID)
            END AS customerTypeInfo, CONCAT_WS(',', customer.EmailAddress, customer.PhoneNum, customer.StreetAdd,
            customer.City, customer.State, customer.PostalCode) AS customerInfo
            FROM sale
            LEFT JOIN loggedinuser ON
             sale.Username = loggedinuser.Username
            LEFT JOIN customer ON
             customer.Customer_ID = sale.Customer_ID
            LEFT JOIN individual ON
             sale.Customer_ID = individual.Customer_ID
            LEFT JOIN business ON
             sale.Customer_ID = business.Customer_ID
            ) as sale_section
            ON vehicle.VIN = sale_section.VIN
            LEFT JOIN loggedinuser
            ON vehicle.Username = loggedinuser.Username
            WHERE
            vehicle.VIN = %s;"""

    @property
    def show_convertible_details(self):
        return """SELECT vehicle.VIN, "Convertible" AS type, vehicle.ModelYear,
            vehicle.ModelName, vehicle.ManufacturerName, vehicles_with_colors_grouped.Color,
            ROUND(vehicle.InvoicePrice*1.2, 2) AS ListPrice, vehicle.OptionalDescription as Description,
            convertible.RoofType, convertible.BackSeatCount,
            vehicle.InvoicePrice, vehicle.DateAdded, CONCAT_WS(' ', loggedinuser.FirstName, loggedinuser.LastName),
            sale_section.SoldPrice, sale_section.PurchaseDate, CONCAT_WS(' ', sale_section.FirstName, sale_section.LastName),
            sale_section.customerTypeInfo, sale_section.customerInfo,
            CASE WHEN sale_section.VIN IS NULL
            THEN 'Unsold' ELSE 'Sold'
            END AS Sale_Condition
            FROM vehicle
            LEFT JOIN convertible
            ON convertible.VIN = vehicle.VIN
            LEFT JOIN
            (
            SELECT vehiclecolor.VIN, GROUP_CONCAT(vehiclecolor.Color
            ORDER BY Color ASC) as Color
            FROM vehiclecolor
            GROUP BY VIN
            ) as vehicles_with_colors_grouped
            ON vehicles_with_colors_grouped.VIN = vehicle.VIN
            LEFT JOIN (
            SELECT sale.VIN, loggedinuser.FirstName, loggedinuser.LastName, sale.PurchaseDate, sale.SoldPrice,
            CASE WHEN individual.Customer_ID IS NOT NULL
            THEN ( SELECT CONCAT_WS(',', individual.Customer_ID, individual.FirstName, individual.LastName) AS IndividualInfo
            FROM individual WHERE sale.Customer_ID = individual.Customer_ID)
            ELSE (SELECT CONCAT_WS(',', business.Customer_ID, business.BusinessName, business.ContactTitle, business.Contact_FirstName,
            business.Contact_LastName) AS BusinessInfo FROM business WHERE sale.Customer_ID = business.Customer_ID)
            END AS customerTypeInfo, CONCAT_WS(',', customer.EmailAddress, customer.PhoneNum, customer.StreetAdd,
            customer.City, customer.State, customer.PostalCode) AS customerInfo
            FROM sale
            LEFT JOIN loggedinuser ON
             sale.Username = loggedinuser.Username
            LEFT JOIN customer ON
             customer.Customer_ID = sale.Customer_ID
            LEFT JOIN individual ON
             sale.Customer_ID = individual.Customer_ID
            LEFT JOIN business ON
             sale.Customer_ID = business.Customer_ID
            ) AS sale_section
            ON vehicle.VIN = sale_section.VIN
            LEFT JOIN loggedinuser
            ON vehicle.Username = loggedinuser.Username
            WHERE
            vehicle.VIN = %s;"""

    @property
    def find_repair_records(self):
        return """
        SELECT
        customer_section.customerTypeInfo,
        CONCAT_WS(' ', loggedinuser.Firstname, loggedinuser.LastName),
        repair.startDate, repair.endDate,
        repair.Odometer, repair.Description, repair.isFinished,
        repair.LaborCharge,
        ROUND(part.Quantity * part.Price, 2),

        part.VendorName, part.PartNumber,
        part.Quantity, part.Price
        From repair
        LEFT JOIN part
        ON repair.VIN = part.VIN
        AND repair.StartDate = part.StartDate
        LEFT JOIN loggedinuser
        ON repair.Username = loggedinuser.Username
        LEFT JOIN (
            SELECT customer.Customer_ID, CASE WHEN individual.Customer_ID IS NOT NULL
            THEN ( SELECT CONCAT_WS(',', individual.Customer_ID, individual.FirstName, individual.LastName) AS IndividualInfo
            FROM individual WHERE customer.Customer_ID = individual.Customer_ID)
            ELSE (SELECT CONCAT_WS(',', business.Customer_ID, business.BusinessName) AS BusinessInfo FROM business WHERE customer.Customer_ID = business.Customer_ID)
            END AS customerTypeInfo
            FROM customer
            LEFT JOIN individual
            ON individual.Customer_ID = customer.Customer_ID
            LEFT JOIN business
            ON business.Customer_ID = customer.Customer_ID

        ) AS customer_section
        ON repair.Customer_ID = customer_section.Customer_ID
        WHERE
        repair.VIN = %s
        """

    @property
    def check_vehicle_part_exist(self):
        return """
        SELECT CASE WHEN part.VIN is null 
        THEN 0 ELSE 1
        END AS status
        FROM repair left join part on 
        repair.VIN = part.vin 
        where 
        repair.VIN = %s;
        """

    @property
    def check_unfinished_repair_exist(self):
        return """
        SELECT repair.IsFinished, repair.VIN, repair.StartDate
        FROM repair
        WHERE 
        repair.VIN = %s AND 
        repair.IsFinished = 0
        ;
        """

    @property
    def check_new_repair_valid(self):
        return """
        SELECT repair.VIN
        FROM repair
        WHERE 
        repair.VIN = %s AND 
        repair.StartDate = %s
        ;
        """

    @property
    def check_new_part_valid(self):
        return """
          SELECT part.VIN
          FROM part
          WHERE 
          part.VIN = %s AND 
          part.StartDate = %s AND 
          part.PartNumber = %s
          ;
          """

    @property
    def insert_repair(self):
        return """
        INSERT INTO repair(VIN, StartDate, Customer_ID, Description, LaborCharge, Odometer, 
        Username)
        VALUES(%(VIN)s, %(startDate)s, %(customerID)s, %(desc)s, %(charge)s, %(odometer)s, %(username)s);
         """

    @property
    def insert_part(self):
        return """
         INSERT INTO part(VIN, StartDate, PartNumber, Customer_ID, VendorName, Quantity, Price)
         VALUES(%(VIN)s, %(startDate)s, %(part_number)s, %(customerID)s, %(vendor_name)s, %(quantity)s, %(price)s);
          """

    @property
    def update_labor_charge(self):
        return """
             UPDATE repair 
             SET repair.LaborCharge = %(charge)s
             WHERE repair.VIN = %(VIN)s AND repair.StartDate = %(startDate)s;
             """

    @property
    def complete_repair(self):
        return """
                 UPDATE repair 
                 SET repair.ISFinished = 1, repair.EndDate = %s
                 WHERE repair.VIN = %s AND repair.StartDate = %s;
                 """

    @property
    def Sale_by_color(self):
        return """
                   SELECT
                   color.Color as Color,
                   ifnull(cte.30_days_Sold_Number,0) as 30_days_Sold_Number,
                   ifnull(cte.1_year_Sold_Number,0) as 1_year_Sold_Number,
                   ifnull(cte.Total_Sold_Number,0) as Total_Sold_Number
                   FROM color
                   LEFT JOIN (
                   SELECT
                   vehiclecolor.Color,
                   COUNT(case when PurchaseDate >= date_add((select max(PurchaseDate) from sale),interval -30 day) then sale.VIN END) AS 30_days_Sold_Number,
                   COUNT(case when PurchaseDate >= date_add((select max(PurchaseDate) from sale),interval -1 year) then sale.VIN END) AS 1_year_Sold_Number,
                   COUNT(sale.VIN) AS Total_Sold_Number
                   FROM sale
                   LEFT JOIN vehicle
                   ON vehicle.VIN = sale.VIN
                   LEFT JOIN vehiclecolor
                   ON vehiclecolor.VIN = vehicle.VIN
                   WHERE Color like '%'
                   GROUP BY Color
                   ORDER BY Color) AS cte
                   ON color.Color = cte.Color
                   UNION(
                   SELECT
                   'Multiple' as Color,
                   COUNT(case when PurchaseDate >= date_add((select max(PurchaseDate) from sale),interval -30 day) then sale.VIN END) AS 30_days_Sold_Number,
                   COUNT(case when PurchaseDate >= date_add((select max(PurchaseDate) from sale),interval -1 year) then sale.VIN END) AS 1_year_Sold_Number,
                   COUNT(sale.VIN) AS Total_Sold_Number
                   FROM sale
                   LEFT JOIN
                   vehiclecolor
                   ON vehiclecolor.VIN = sale.VIN
                   WHERE Color like '%,%');
                    """

    @property
    def Sale_by_type(self):
        return """SELECT
                   VehicleType as Type,
                   COUNT(case when PurchaseDate >= date_add((select max(PurchaseDate) from sale),interval -30 day) then sale.VIN END) AS 30_days_Sold_Number,
                   COUNT(case when PurchaseDate >= date_add((select max(PurchaseDate) from sale),interval -1 year) then sale.VIN END) AS 1_year_Sold_Number,
                   COUNT(sale.VIN) AS Total_Sold_Number
                   FROM sale
                   LEFT JOIN
                   (SELECT suv.VIN, 'SUV' as VehicleType FROM suv
                   UNION ALL
                   SELECT truck.VIN, 'Truck' as VehicleType FROM truck
                   UNION ALL
                   SELECT vanminivan.VIN, 'Van' as VehicleType FROM vanminivan
                   UNION ALL
                   SELECT car.VIN, 'Car' as VehicleType FROM car
                   UNION ALL
                   SELECT convertible.VIN, 'Convertible' as VehicleType FROM convertible) as Vehicles_with_types
                   ON Vehicles_with_types.VIN = sale.VIN
                   GROUP BY Type
                   ORDER BY Type;
                   """

    @property
    def Sale_by_manufacturer(self):
        return """
                   SELECT
                   vehicle.ManufacturerName,
                   COUNT( case when PurchaseDate >= date_add((select max(PurchaseDate) from sale),interval -30 day) then sale.VIN END ) AS 30_days_Sold_Number,
                   COUNT( case when PurchaseDate >= date_add((select max(PurchaseDate) from sale),interval -1 year) then sale.VIN END ) AS 1_year_Sold_Number,
                   COUNT( sale.VIN ) AS Total_Sold_Number
                   FROM sale
                   LEFT JOIN vehicle
                   ON vehicle.VIN = sale.VIN
                   GROUP BY 1
                   ORDER BY 1;
                   """

    @property
    def below_cost_sales(self):
        return """SELECT
                  sale.PurchaseDate,
                  vehicle.InvoicePrice,
                  sale.SoldPrice,
                  ROUND(sale.SoldPrice/vehicle.InvoicePrice, 4) AS Ratio,
                  IF(business.BusinessName IS NULL, CONCAT(individual.FirstName, " ", individual.LastName), business.BusinessName) AS CustomerName,
                  CONCAT(loggedinuser.FirstName, " ", loggedinuser.LastName) AS SalePersonName
                  FROM Sale
                  LEFT JOIN
                  business
                  ON business.Customer_ID = sale.Customer_ID
                  LEFT JOIN
                  individual
                  ON individual.Customer_ID = sale.Customer_ID
                  LEFT JOIN
                  vehicle
                  ON vehicle.VIN = sale.VIN
                  LEFT JOIN
                  salesperson
                  ON salesperson.Username = sale.Username
                  LEFT JOIN
                  loggedinuser
                  ON loggedinuser.Username = salesperson.Username
                  WHERE ROUND(sale.SoldPrice/vehicle.InvoicePrice, 6) < 1.0
                  ORDER BY
                  sale.PurchaseDate DESC,
                  Ratio DESC;
                """

    @property
    def average_time_inventory(self):
        return """  SELECT VehicleType, round(AVG(datediff(Sale.PurchaseDate, Vehicle.DateAdded)),0) as 'AvgTime(in day)'
                    FROM Sale
                    INNER JOIN Vehicle
                    ON Sale.VIN = Vehicle.VIN
                    LEFT JOIN
                    (select VIN, 'Car' as VehicleType
                    from Car
                    union all
                    select VIN, 'Truck' as VehicleType
                    from Truck
                    union all
                    select VIN, 'SUV' as VehicleType
                    from SUV
                    union all
                    select VIN, 'Van' as VehicleType
                    from VanMinivan
                    union all
                    select VIN, 'Convertible' as VehicleType
                    from Convertible) sub
                    on Sale.VIN = sub.VIN
                    group by VehicleType
                    order by 2;
                """

    @property
    def part_statistics(self):
        return """SELECT
                  Part.VendorName,
                  sum(Part.Quantity) as TotalN,
                  round(sum(Part.Quantity*Part.Price),2) as TotalD
                  FROM Part
                  GROUP BY VendorName;
                """

    @property
    def monthly_sales_summary(self):
        return """  SELECT
                    date_format(Sale.PurchaseDate, '%Y-%m') as 'Year_month',
                    count(Vehicle.VIN) as VehiclesNo,
                    round(sum(Sale.SoldPrice),0) as TotalSales,
                    round(sum(Sale.SoldPrice - Vehicle.InvoicePrice),0) as TotalNet,
                    ROUND(sum(Sale.SoldPrice)*100/sum(Vehicle.InvoicePrice), 0) as Ratio
                    FROM Sale
                    INNER JOIN Vehicle
                    ON Sale.VIN = Vehicle.VIN
                    GROUP BY 1
                    ORDER BY 1 desc;
                """

    @property
    def monthly_sales_drilldown(self):
        return """  SELECT
                    LoggedInUser.FirstName,
                    LoggedInUser.LastName,
                    count(Sale.VIN) as VehiclesNo,
                    round(sum(Sale.SoldPrice),2) as TotalSales
                    FROM Sale
                    INNER JOIN SalesPerson
                    ON Sale.Username = SalesPerson.Username
                    INNER JOIN LoggedInUser
                    ON SalesPerson.Username = LoggedInUser.Username
                    WHERE date_format(Sale.PurchaseDate, '%%Y-%%m') = %s
                    group by 1,2
                    order by 3 desc, 4 desc
                    limit 1;
                """

    @property
    def gross_customer_income(self):
        return  """
                SELECT
                SaleTable.CustomerName,
                RepairTable.FirstRepairDate,
                SaleTable.FirstSaleDate,
                RepairTable.LastRepairDate,
                SaleTable.LastSaleDate,
                SaleTable.NumofSale,
                RepairTable.NumofRepair,
                ROUND(IF(SaleTable.TotalSale IS NULL, 0, SaleTable.TotalSale), 2) AS TotalSale,
                ROUND(IF(RepairTable.TotalRepairCost IS NULL, 0, RepairTable.TotalRepairCost), 2) AS TotalRepairCost,
                ROUND((IF(SaleTable.TotalSale IS NULL, 0, SaleTable.TotalSale) + IF(RepairTable.TotalRepairCost IS NULL, 0, RepairTable.TotalRepairCost)), 2) AS GrossIncome,
                SaleTable.Customer_ID
                FROM
                (
                    SELECT
                    IF(business.BusinessName IS NULL, CONCAT(individual.FirstName, " ", individual.LastName), business.BusinessName) AS CustomerName,
                    SUM(sale.SoldPrice) AS TotalSale,
                    COUNT(*) AS NumofSale,
                    MIN(sale.PurchaseDate) AS FirstSaleDate,
                    MAX(sale.PurchaseDate) AS LastSaleDate,
                    MIN(sale.Customer_ID) AS Customer_ID
                    FROM sale
                    Left JOIN business
                    ON business.Customer_ID = sale.Customer_ID
                    Left JOIN individual
                    ON individual.Customer_ID = sale.Customer_ID
                    GROUP BY CustomerName
                ) AS SaleTable
                LEFT JOIN
                (
                    SELECT
                    IF(business.BusinessName IS NULL, CONCAT(individual.FirstName, " ", individual.LastName), business.BusinessName) AS CustomerName,
                    SUM(repair_part.LaborCharge + repair_part.PartCost) AS TotalRepairCost,
                    COUNT(*) AS NumofRepair,
                    MIN(repair_part.StartDate) AS FirstRepairDate,
                    MAX(repair_part.StartDate) AS LastRepairDate
                    FROM
                        (
                            SELECT
                            repair.Customer_ID AS Customer_ID,
                            repair.VIN AS VIN,
                            repair.StartDate AS StartDate,
                            repair.EndDate AS EndDate,
                            repair.LaborCharge AS LaborCharge,
                            (IF(part.Price IS NULL, 0, part.Price) * IF(part.Quantity IS NULL, 0, part.Quantity)) AS PartCost
                            FROM repair
                            LEFT JOIN part
                            ON part.VIN = repair.VIN AND part.Customer_ID = repair.Customer_ID AND part.StartDate = repair.StartDate
                        ) AS repair_part
                        LEFT JOIN business
                        ON business.Customer_ID = repair_part.Customer_ID
                        Left JOIN individual
                        ON individual.Customer_ID = repair_part.Customer_ID
                        GROUP BY CustomerName
                ) AS RepairTable
                ON SaleTable.CustomerName = RepairTable.CustomerName
                ORDER BY
                GrossIncome DESC,
                SaleTable.LastSaleDate DESC,
                RepairTable.LastRepairDate DESC;
                """

    @property
    def gross_customer_income_salerecords(self):
        return  """
                SELECT
                sale.PurchaseDate,
                sale.SoldPrice,
                vehicle.VIN,
                vehicle.ModelYear,
                manufacturer.ManufacturerName,
                vehicle.ModelName,
                CONCAT(loggedinuser.FirstName, " ", loggedinuser.LastName) AS SalePersonName,
                Sale.Customer_ID
                FROM sale
                LEFT JOIN vehicle
                ON vehicle.VIN = sale.VIN
                LEFT JOIN manufacturer
                ON manufacturer.ManufacturerName = vehicle.ManufacturerName
                LEFT JOIN salesperson
                ON salesperson.Username = sale.Username
                LEFT JOIN loggedinuser
                ON loggedinuser.Username = salesperson.Username
                WHERE sale.Customer_ID = %s
                ORDER BY
                sale.PurchaseDate DESC,
                vehicle.VIN ASC;

                """

    @property
    def gross_customer_income_repairrecords(self):
        return  """
                SELECT
                repair_part.StartDate,
                repair_part.EndDate,
                vehicle.VIN,
                repair_part.Odometer,
                ROUND(IF(repair_part.PartCost IS NULL, 0, repair_part.PartCost), 2),
                ROUND(IF(repair_part.LaborCharge IS NULL, 0, repair_part.LaborCharge), 2),
                (ROUND(IF(repair_part.PartCost IS NULL, 0, repair_part.PartCost), 2) + ROUND(IF(repair_part.LaborCharge IS NULL, 0, repair_part.LaborCharge), 2)) AS TotalRepairCost,
                CONCAT(loggedinuser.FirstName, " ", loggedinuser.LastName) AS ServiceWriterName,
                repair_part.isFinished
                FROM
                (
                    SELECT
                    repair.Customer_ID AS Customer_ID,
                    repair.Username AS Username,
                    repair.StartDate AS StartDate,
                    repair.EndDate AS EndDate,
                    repair.VIN AS VIN,
                    repair.Odometer AS Odometer,
                    (IF(part.Price IS NULL, 0, part.Price) * IF(part.Quantity IS NULL, 0, part.Quantity)) AS PartCost,
                    repair.LaborCharge AS LaborCharge,
                    repair.IsFinished AS isFinished
                    FROM repair
                    LEFT JOIN part
                    ON part.VIN = repair.VIN AND part.Customer_ID = repair.Customer_ID AND part.StartDate = repair.StartDate
                ) AS repair_part
                LEFT JOIN vehicle
                ON vehicle.VIN = repair_part.VIN
                LEFT JOIN servicewriter
                ON servicewriter.Username = repair_part.Username
                LEFT JOIN loggedinuser
                ON loggedinuser.Username = servicewriter.Username
                WHERE repair_part.Customer_ID = %s
                ORDER BY
                    repair_part.isFinished,
                    repair_part.StartDate DESC,
                    repair_part.EndDate DESC,
                    Vehicle.vin ASC;
                """

    @property
    def repair_by_manufacturer(self):
        return  """
                SELECT
                manufacturer.ManufacturerName,
                COUNT(*) AS CountofRepairs,
                ROUND(SUM(IF(repair_part.PartCost IS NULL, 0, repair_part.PartCost)), 2) AS SumofPartCost,
                ROUND(SUM(IF(repair_part.LaborCharge IS NULL, 0, repair_part.LaborCharge)), 2) AS SumofLaborCost,
                ROUND(SUM(IF(repair_part.PartCost IS NULL, 0, repair_part.PartCost) + IF(repair_part.LaborCharge IS NULL, 0, repair_part.LaborCharge)), 2) AS SumofTotalCost
                FROM
                (
                    SELECT
                    repair.VIN AS VIN,
                    repair.StartDate AS StartDate,
                    repair.EndDate AS EndDate,
                    repair.LaborCharge AS LaborCharge,
                    (IF(part.Price IS NULL, 0, part.Price) * IF(part.Quantity IS NULL, 0, part.Quantity)) AS PartCost
                    FROM repair
                    LEFT JOIN part
                    ON part.VIN = repair.VIN AND part.Customer_ID = repair.Customer_ID AND part.StartDate = repair.StartDate
                ) AS repair_part
                LEFT JOIN vehicle
                ON vehicle.VIN = repair_part.VIN
                LEFT JOIN manufacturer
                ON manufacturer.ManufacturerName = vehicle.ManufacturerName
                GROUP BY manufacturer.ManufacturerName
                ORDER BY manufacturer.ManufacturerName;
                """

    @property
    def repair_by_type(self):
        return  """
                SELECT
                vehicles_with_types.VehicleType AS VechicleType,
                COUNT(*) AS VTRepairCount,
                ROUND(SUM(IF(repair_part.PartCost IS NULL, 0, repair_part.PartCost)), 2) AS VTPartCost,
                ROUND(SUM(IF(repair_part.LaborCharge IS NULL, 0, repair_part.LaborCharge)), 2) AS VTLaborCost,
                ROUND(SUM(IF(repair_part.PartCost IS NULL, 0, repair_part.PartCost) + IF(repair_part.LaborCharge IS NULL, 0, repair_part.LaborCharge)), 2) AS VTTotalCost,
                manufacturer.ManufacturerName
                FROM
                (
                    SELECT
                    repair.VIN AS VIN,
                    repair.LaborCharge AS LaborCharge,
                    repair.IsFinished AS isFinished,
                    (IF(part.Price IS NULL, 0, part.Price) * IF(part.Quantity IS NULL, 0, part.Quantity)) AS PartCost
                    FROM repair
                    LEFT JOIN part
                    ON part.VIN = repair.VIN AND part.Customer_ID = repair.Customer_ID AND part.StartDate = repair.StartDate
                    WHERE repair.isFinished = 1
                ) AS repair_part
                LEFT JOIN vehicle
                ON vehicle.VIN = repair_part.VIN
                LEFT JOIN
                (
                    SELECT suv.VIN, 'SUV' as VehicleType FROM suv
                    UNION ALL
                    SELECT truck.VIN, 'Truck' as VehicleType FROM truck
                    UNION ALL
                    SELECT vanminivan.VIN, 'Van' as VehicleType FROM vanminivan
                    UNION ALL
                    SELECT car.VIN, 'Car' as VehicleType FROM car
                    UNION ALL
                    SELECT convertible.VIN, 'Convertible' as VehicleType FROM convertible
                ) as vehicles_with_types
                ON vehicles_with_types.VIN = vehicle.VIN
                INNER JOIN manufacturer
                ON manufacturer.ManufacturerName = vehicle.ManufacturerName
                WHERE manufacturer.ManufacturerName = %s
                GROUP BY
                    vehicles_with_types.VehicleType
                ORDER BY
                    vehicles_with_types.VehicleType,
                    VTRepairCount DESC;
                """

    @property
    def repair_by_model(self):
        return  """
                SELECT
                vehicle.ModelName,
                COUNT(*) AS VTRepairCount,
                ROUND(SUM(IF(repair_part.PartCost IS NULL, 0, repair_part.PartCost)), 2) AS VTPartCost,
                ROUND(SUM(IF(repair_part.LaborCharge IS NULL, 0, repair_part.LaborCharge)), 2) AS VTLaborCost,
                ROUND(SUM(IF(repair_part.PartCost IS NULL, 0, repair_part.PartCost) + IF(repair_part.LaborCharge IS NULL, 0, repair_part.LaborCharge)), 2) AS VTTotalCost
                FROM
                (
                    SELECT
                    repair.VIN AS VIN,
                    repair.LaborCharge AS LaborCharge,
                    repair.IsFinished AS isFinished,
                    (IF(part.Price IS NULL, 0, part.Price) * IF(part.Quantity IS NULL, 0, part.Quantity)) AS PartCost
                    FROM repair
                    LEFT JOIN part
                    ON part.VIN = repair.VIN AND part.Customer_ID = repair.Customer_ID AND part.StartDate = repair.StartDate
                    WHERE repair.isFinished = 1
                ) AS repair_part
                LEFT JOIN vehicle
                ON vehicle.VIN = repair_part.VIN
                LEFT JOIN
                (
                    SELECT suv.VIN, 'SUV' as VehicleType FROM suv
                    UNION ALL
                    SELECT truck.VIN, 'Truck' as VehicleType FROM truck
                    UNION ALL
                    SELECT vanminivan.VIN, 'Van' as VehicleType FROM vanminivan
                    UNION ALL
                    SELECT car.VIN, 'Car' as VehicleType FROM car
                    UNION ALL
                    SELECT convertible.VIN, 'Convertible' as VehicleType FROM convertible
                ) as vehicles_with_types
                ON vehicles_with_types.VIN = vehicle.VIN
                INNER JOIN manufacturer
                ON manufacturer.ManufacturerName = vehicle.ManufacturerName
                WHERE manufacturer.ManufacturerName = %s AND vehicles_with_types.VehicleType = %s
                GROUP BY
                    vehicle.ModelName
                ORDER BY
                    vehicle.ModelName,
                    VTRepairCount DESC;
                """

    @property
    def add_color(self):
        return """insert into color values ( %(color)s );"""

    @property
    def add_a_vehicle(self):
        return """
        insert into vehicle
        (VIN, ManufacturerName, Username, ModelName, ModelYear, InvoicePrice, DateAdded, OptionalDescription)
        values ( %(vin)s, %(manufacturer)s, %(userName)s, %(modelName)s, %(modelYear)s, %(invoicePrice)s, %(dateAdded)s, %(description)s );
        """

    @property
    def add_a_suv(self):
        return """
        insert into suv
        (VIN, NoOfCupHolders, DrivetrainType)
        values ( %(vin)s, %(noOfCupHolders)s, %(drivetrainType)s );
        """

    @property
    def add_a_car(self):
        return """
        insert into car
        (VIN, NoOfDoors)
        values ( %(vin)s, %(numberOfDoors)s );
        """

    @property
    def add_a_truck(self):
        return """
        insert into truck
        (VIN, NoOfRearAxies, CargoCapacity, CargoCoverType)
        values ( %(vin)s, %(noOfRearAxles)s, %(cargoCapacity)s, %(cargoCoverType)s );
        """

    @property
    def add_a_van(self):
        return """
        insert into vanminivan
        (VIN, HasDriversSideBackDoor)
        values ( %(vin)s, %(hasBackDoor)s );
        """

    @property
    def add_a_manufacture(self):
        return """
                insert into manufacturer
                values ( %s );
                """

    @property
    def add_a_convertible(self):
        return """
        insert into convertible
        (VIN, BackSeatCount, RoofType)
        values ( %(vin)s, %(backSeatCount)s, %(roofType)s );
        """

    @property
    def get_manufacture(self):
        return """
        select ManufacturerName from manufacturer
        where ManufacturerName = %s
        """

    @property
    def add_a_sale(self):
        return """
        insert into sale
        (VIN, Username, Customer_ID, PurchaseDate, SoldPrice)
        values ( %s, %s, %s, %s, %s );
        """

    @property
    def add_vehicle_color(self):
        return """
        insert into vehiclecolor
        (VIN, COLOR)
        values ( %s, %s);
        """
