from db import get_connection

conn = get_connection()
cursor = conn.cursor()

print("Creating tables...")

# -----------------------------
# CUSTOMER
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Customer (
customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT UNIQUE,
phone TEXT,
default_address TEXT
)
""")

# -----------------------------
# EMPLOYEE
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Employee (
employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
role TEXT,
email TEXT,
phone TEXT
)
""")

# -----------------------------
# INQUIRY
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Inquiry (
inquiry_id INTEGER PRIMARY KEY AUTOINCREMENT,
customer_id INTEGER,
employee_id INTEGER,
subject TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY(customer_id) REFERENCES Customer(customer_id),
FOREIGN KEY(employee_id) REFERENCES Employee(employee_id)
)
""")

# -----------------------------
# PACKAGE
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Package (
package_id INTEGER PRIMARY KEY AUTOINCREMENT,
customer_id INTEGER,
weight_lbs REAL,
length_in REAL,
width_in REAL,
height_in REAL,
declared_value REAL,
special_cargo TEXT,
delivery_location TEXT,
FOREIGN KEY(customer_id) REFERENCES Customer(customer_id)
)
""")

# -----------------------------
# VEHICLE
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Vehicle (
vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
plate_number TEXT UNIQUE,
vehicle_type TEXT,
max_capacity_lbs REAL
)
""")

# -----------------------------
# SHIPMENT
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Shipment (
shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
package_id INTEGER,
employee_id INTEGER,
vehicle_id INTEGER,
delivery_location TEXT,
distance_miles REAL,
status TEXT,
expected_delivery_date TEXT,
price_estimate REAL,
FOREIGN KEY(package_id) REFERENCES Package(package_id),
FOREIGN KEY(employee_id) REFERENCES Employee(employee_id),
FOREIGN KEY(vehicle_id) REFERENCES Vehicle(vehicle_id)
)
""")

# -----------------------------
# PAYMENT
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS Payment (
payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
shipment_id INTEGER,
payment_date TEXT,
amount REAL,
method TEXT,
FOREIGN KEY(shipment_id) REFERENCES Shipment(shipment_id)
)
""")

conn.commit()

print("Tables created successfully.")
print("Inserting dataset...")

# ---------------------------------------
# INSERT CUSTOMER DATA
# ---------------------------------------
customers = [
('Joe', 'joe@gmail.com', '123', '145 main st'),
('Buse', 'buse@gmail.com', '234', '202 oakland st'),
('Max', 'max@gmail.com', '345', '106 virginia st'),
('Bob', 'bob@gmail.com', '456', '904 penn ave'),
('Tom', 'tom@gmail.com', '567', '1092 hillside ave'),
('Sam', 'sam@gmail.com', '678', '456 north st'),
('Anna', 'anna@gmail.com', '789', '412 pitt ave')
]

cursor.executemany("""
INSERT INTO Customer (name, email, phone, default_address)
VALUES (?, ?, ?, ?)
""", customers)


# ---------------------------------------
# INSERT EMPLOYEE DATA
# ---------------------------------------
employees = [
('Steve', 'Driver', 'steve@gmail.com', '890'),
('Joe', 'Support', 'joe@gmail.com', None),
('Darla', 'Driver', 'darla@gmail.com', '120')
]

cursor.executemany("""
INSERT INTO Employee (name, role, email, phone)
VALUES (?, ?, ?, ?)
""", employees)


# ---------------------------------------
# INSERT INQUIRY DATA
# ---------------------------------------
inquiries = [
(1, 2, 'Package delayed', '2025-11-08 10:30:00'),
(2, 1, 'Billing question', '2025-11-09 14:15:00'),
(3, 3, 'Damage report', '2025-11-07 09:00:00'),
(4, 2, 'Change delivery address', '2025-11-06 16:45:00'),
(5, 1, 'Payment confirmation', '2025-11-05 11:20:00'),
(6, 3, 'Lost package', '2025-11-08 12:10:00'),
(7, 2, 'Shipment status inquiry', '2025-11-09 15:50:00'),
]

cursor.executemany("""
INSERT INTO Inquiry (customer_id, employee_id, subject, created_at)
VALUES (?, ?, ?, ?)
""", inquiries)


# ---------------------------------------
# INSERT PACKAGE DATA
# ---------------------------------------
packages = [
(1, 10.50, 12.00, 8.00, 6.00, 150.00, 'No'),
(2, 5.00, 10.00, 6.00, 4.00, 75.00, 'Yes'),
(3, 20.00, 24.00, 12.00, 10.00, 300.00, 'No'),
(4, 7.50, 14.00, 10.00, 8.00, 120.00, 'Yes'),
(5, 15.00, 20.00, 14.00, 12.00, 250.00, 'No'),
(6, 8.00, 16.00, 10.00, 9.00, 100.00, 'No'),
(7, 12.00, 18.00, 12.00, 10.00, 200.00, 'Yes')
]

cursor.executemany("""
INSERT INTO Package (customer_id, weight_lbs, length_in, width_in, height_in, declared_value, special_cargo)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", packages)


# ---------------------------------------
# INSERT VEHICLE DATA
# ---------------------------------------
vehicles = [
(111, 'van202', 'Truck', 8000.00),
(222, 'pitt2026', 'Truck', 8000.00),
(333, 'trk333', 'Van', 2000.00),
(444, 'penn444', 'Van', 2000.00)
]

cursor.executemany("""
INSERT INTO Vehicle (vehicle_id, plate_number, vehicle_type, max_capacity_lbs)
VALUES (?, ?, ?, ?)
""", vehicles)


# ---------------------------------------
# INSERT SHIPMENT DATA
# ---------------------------------------
shipments = [
(1, 1, 111, '145 Main St', 12.50, 'Pending', '2025-11-12', None),
(2, 2, 222, '202 Oakland St', 8.00, 'In Transit', '2025-11-13', None),
(3, 3, 333, '106 Virginia St', 20.00, 'Delivered', '2025-11-10', None),
(4, 4, 111, '904 Penn Ave', 15.00, 'Pending', '2025-11-14', None),
(5, 5, 222, '1092 Hillside Ave', 18.50, 'In Transit', '2025-11-15', None),
(6, 6, 333, '456 North St', 10.00, 'Pending', '2025-11-16', None),
(7, 7, 111, '412 Pitt Ave', 14.00, 'Delivered', '2025-11-11', None)
]

cursor.executemany("""
INSERT INTO Shipment (package_id, employee_id, vehicle_id, delivery_location, distance_miles, status, expected_delivery_date, price_estimate)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", shipments)


# ---------------------------------------
# INSERT PAYMENT DATA
# ---------------------------------------
payments = [
(1, 1, '2025-11-12', 50.00, 'Credit'),
(2, 2, '2025-11-13', 35.00, 'Debit'),
(3, 3, '2025-11-10', 75.00, 'PayPal'),
(4, 4, '2025-11-14', 60.00, 'Cash'),
(5, 5, '2025-11-15', 80.00, 'Credit'),
(6, 6, '2025-11-16', 40.00, 'Debit'),
(7, 7, '2025-11-11', 55.00, 'PayPal')
]

cursor.executemany("""
INSERT INTO Payment (payment_id, shipment_id, payment_date, amount, method)
VALUES (?, ?, ?, ?, ?)
""", payments)


conn.commit()

cursor.close()
conn.close()

print("Database created and populated successfully!")