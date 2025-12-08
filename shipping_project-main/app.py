from flask import Flask, render_template, request, redirect, session, flash
from db import get_connection
import os
import subprocess

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # Change this in production!

# Initialize database on first run
def init_db():
    if not os.path.exists('ground_shipping.db'):
        print("Database not found. Creating database...")
        subprocess.run(['python', 'create_db.py'])
        print("Database created successfully!")

init_db()


# LOGIN PAGE
@app.route("/")
def home():
    return render_template("login.html")

# CUSTOMER LOGIN
@app.route("/customer_login", methods=["GET", "POST"])
def customer_login():
    if request.method == "POST":
        email = request.form["email"]
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Customer WHERE email = ?", (email,))
        customer = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if customer:
            session['user_type'] = 'customer'
            session['user_id'] = customer['customer_id']
            session['user_name'] = customer['name']
            session['user_email'] = customer['email']
            return redirect("/customer_dashboard")
        else:
            flash("Email not found. Please check your email or contact support.")
            return redirect("/customer_login")
    
    return render_template("customer_login.html")

# EMPLOYEE LOGIN
@app.route("/employee_login", methods=["GET", "POST"])
def employee_login():
    if request.method == "POST":
        email = request.form["email"]
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Employee WHERE email = ?", (email,))
        employee = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if employee:
            session['user_type'] = 'employee'
            session['user_id'] = employee['employee_id']
            session['user_name'] = employee['name']
            session['user_email'] = employee['email']
            session['user_role'] = employee['role']
            return redirect("/employee_dashboard")
        else:
            flash("Email not found. Please check your email or contact support.")
            return redirect("/employee_login")
    
    return render_template("employee_login.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# CUSTOMER DASHBOARD
@app.route("/customer_dashboard")
def customer_dashboard():
    if 'user_type' not in session or session['user_type'] != 'customer':
        return redirect("/")
    
    customer_id = session['user_id']
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get customer's packages and shipments
    cursor.execute("""
        SELECT Package.package_id, Shipment.shipment_id, Shipment.delivery_location, 
               Shipment.status, Shipment.expected_delivery_date
        FROM Package
        LEFT JOIN Shipment ON Package.package_id = Shipment.package_id
        WHERE Package.customer_id = ?
        ORDER BY Package.package_id DESC
    """, (customer_id,))
    shipments = cursor.fetchall()
    
    # Get customer's payments
    cursor.execute("""
        SELECT Payment.payment_id, Payment.shipment_id, Payment.amount, 
               Payment.method, Payment.payment_date
        FROM Payment
        JOIN Shipment ON Payment.shipment_id = Shipment.shipment_id
        JOIN Package ON Shipment.package_id = Package.package_id
        WHERE Package.customer_id = ?
        ORDER BY Payment.payment_date DESC
    """, (customer_id,))
    payments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("customer_dashboard.html", shipments=shipments, payments=payments)

# EMPLOYEE DASHBOARD
@app.route("/employee_dashboard")
def employee_dashboard():
    if 'user_type' not in session or session['user_type'] != 'employee':
        return redirect("/")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all shipments
    cursor.execute("""
        SELECT Shipment.shipment_id, Customer.name, Shipment.delivery_location, 
               Shipment.status, Shipment.expected_delivery_date, Employee.name as driver_name
        FROM Shipment
        JOIN Package ON Shipment.package_id = Package.package_id
        JOIN Customer ON Package.customer_id = Customer.customer_id
        LEFT JOIN Employee ON Shipment.employee_id = Employee.employee_id
        ORDER BY Shipment.shipment_id DESC
    """)
    shipments = cursor.fetchall()
    
    # Get all inquiries
    cursor.execute("""
        SELECT Inquiry.inquiry_id, Customer.name, Inquiry.subject, Inquiry.created_at
        FROM Inquiry
        JOIN Customer ON Inquiry.customer_id = Customer.customer_id
        ORDER BY Inquiry.created_at DESC
        LIMIT 10
    """)
    inquiries = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("employee_dashboard.html", shipments=shipments, inquiries=inquiries)



 
#Tracking page
 
@app.route("/tracking", methods=["GET", "POST"])
def tracking():
    result = None
    if request.method == "POST":
        tracking_number = request.form["tracking"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT Shipment.*, Customer.name, Customer.email, 
                              Employee.name as driver_name, Employee.phone as driver_phone,
                              Vehicle.plate_number, Vehicle.vehicle_type
                       FROM Shipment
                       JOIN Package ON Shipment.package_id = Package.package_id
                       JOIN Customer ON Package.customer_id = Customer.customer_id
                       JOIN Employee ON Shipment.employee_id = Employee.employee_id
                       JOIN Vehicle ON Shipment.vehicle_id = Vehicle.vehicle_id
                       WHERE Shipment.shipment_id = ?
                       """, (tracking_number,))
        
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()

    return render_template("tracking.html", result=result)


#Reschedule delivery
@app.route("/reschedule", methods=["GET", "POST"])
def reschedule():
    message = None

    if request.method == "POST":
        shipment_id = request.form["tracking"]
        new_date = request.form["date"]
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
                       UPDATE Shipment
                       SET expected_delivery_date = ?
                       WHERE shipment_id = ?
                       """, (new_date, shipment_id))
        
        conn.commit()
        
        message = "Delivery date updated successfully!"
        
        cursor.close()
        conn.close()

    return render_template("reschedule.html", message=message)


 
# ADD NEW PACKAGE
 
@app.route("/add_shipment", methods=["GET", "POST"])
def add_shipment():
    message = None
    package_id = None

    if request.method == "POST":
        #Package data
        customer_id = request.form["customer_id"]
        weight = request.form["weight"]
        length = request.form["length"]
        width = request.form["width"]
        height = request.form["height"]
        declared_value = request.form["value"]
        special_cargo = request.form.get("special", "No")
        
        conn = get_connection()
        cursor = conn.cursor()
        
        #Insert package
        cursor.execute("""
            INSERT INTO Package (customer_id, weight_lbs, length_in, width_in, height_in, declared_value, special_cargo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (customer_id, weight, length, width, height, declared_value, special_cargo))
        
        package_id = cursor.lastrowid
        
        conn.commit()
        
        message = f"Package #{package_id} created successfully! Now assign it to a shipment."
        
        cursor.close()
        conn.close()

    return render_template("add_shipment.html", message=message, package_id=package_id)


# ASSIGN SHIPMENT
@app.route("/assign_shipment", methods=["GET", "POST"])
def assign_shipment():
    message = None
    tracking_number = None

    if request.method == "POST":
        package_id = request.form["package_id"]
        employee_id = request.form["employee_id"]
        vehicle_id = request.form["vehicle_id"]
        delivery_location = request.form["location"]
        distance = request.form["distance"]
        expected_date = request.form["date"]
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Insert shipment
        cursor.execute("""
            INSERT INTO Shipment (package_id, employee_id, vehicle_id, delivery_location, distance_miles, status, expected_delivery_date)
            VALUES (?, ?, ?, ?, ?, 'Pending', ?)
        """, (package_id, employee_id, vehicle_id, delivery_location, distance, expected_date))
        
        tracking_number = cursor.lastrowid
        
        conn.commit()
        
        message = f"Shipment assigned successfully! Tracking Number: #{tracking_number}"
        
        cursor.close()
        conn.close()

    return render_template("assign_shipment.html", message=message, tracking_number=tracking_number)


 
#Update shipment status
 
@app.route("/update_status", methods=["GET", "POST"])
def update_status():
    message = None
    

    if request.method == "POST":
        shipment_id = request.form["shipment_id"]
        new_status = request.form["status"]
        
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE Shipment
        SET status = ?
        WHERE shipment_id = ?
        """, (new_status, shipment_id))
        
        conn.commit()
        
        message = "Shipment status updated!"
        
        cursor.close()
        conn.close()

    return render_template("update_status.html", message=message)


 
#View all content
 
@app.route("/shipments")
def shipments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Shipment")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("shipments.html", rows=rows)

@app.route("/customers")
def customers():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Customer")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("customers.html", rows=rows)


@app.route("/employees")
def employees():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Employee")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("employees.html", rows=rows)

@app.route("/vehicles")
def vehicles():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Vehicle")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("vehicles.html", rows=rows)


@app.route("/inquiries")
def inquiries():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Inquiry")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("inquiries.html", rows=rows)


# VIEW ALL PAYMENTS
@app.route("/payments")
def payments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Payment.*, Shipment.delivery_location, Customer.name as customer_name
        FROM Payment
        JOIN Shipment ON Payment.shipment_id = Shipment.shipment_id
        JOIN Package ON Shipment.package_id = Package.package_id
        JOIN Customer ON Package.customer_id = Customer.customer_id
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("payments.html", rows=rows)


# MAKE PAYMENT
@app.route("/make_payment", methods=["GET", "POST"])
def make_payment():
    message = None
    payment_id = None
    shipment_info = None
    
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        shipment_id = request.form["shipment_id"]
        amount = request.form["amount"]
        method = request.form["method"]
        
        # Verify shipment exists
        cursor.execute("""
            SELECT Shipment.shipment_id, Customer.name, Shipment.delivery_location, 
                   Shipment.price_estimate, Shipment.status
            FROM Shipment
            JOIN Package ON Shipment.package_id = Package.package_id
            JOIN Customer ON Package.customer_id = Customer.customer_id
            WHERE Shipment.shipment_id = ?
        """, (shipment_id,))
        
        shipment = cursor.fetchone()
        
        if shipment:
            # Insert payment
            cursor.execute("""
                INSERT INTO Payment (shipment_id, payment_date, amount, method)
                VALUES (?, datetime('now'), ?, ?)
            """, (shipment_id, amount, method))
            
            payment_id = cursor.lastrowid
            conn.commit()
            
            message = f"Payment #{payment_id} processed successfully for {shipment['name']}'s shipment!"
            shipment_info = shipment
        else:
            message = "Error: Shipment ID not found. Please check and try again."
        
        cursor.close()
        conn.close()
        return render_template("make_payment.html", message=message, payment_id=payment_id, shipment_info=shipment_info)
    
    # GET request - show available shipments
    cursor.execute("""
        SELECT Shipment.shipment_id, Customer.name, Shipment.delivery_location, 
               Shipment.price_estimate, Shipment.status
        FROM Shipment
        JOIN Package ON Shipment.package_id = Package.package_id
        JOIN Customer ON Package.customer_id = Customer.customer_id
        ORDER BY Shipment.shipment_id DESC
    """)
    
    available_shipments = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template("make_payment.html", message=message, payment_id=payment_id, 
                         shipment_info=shipment_info, available_shipments=available_shipments)



 
# RUN THE APP
 
if __name__ == "__main__":
    app.run(debug=True)