from flask import Flask, render_template, request, redirect
from db import get_connection
import os
import subprocess

app = Flask(__name__)

# Initialize database on first run
def init_db():
    if not os.path.exists('ground_shipping.db'):
        print("Database not found. Creating database...")
        subprocess.run(['python', 'create_db.py'])
        print("Database created successfully!")

init_db()


 
#Homepage
 
@app.route("/")
def home():
    return render_template("index.html")



 
#Tracking page
 
@app.route("/tracking", methods=["GET", "POST"])
def tracking():
    result = None
    if request.method == "POST":
        tracking_number = request.form["tracking"]

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT Shipment.*, Customer.name, Customer.email
                       FROM Shipment
                       JOIN Package ON Shipment.package_id = Package.package_id
                       JOIN Customer ON Package.customer_id = Customer.customer_id
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


 
# ADD NEW SHIPMENT
 
@app.route("/add_shipment", methods=["GET", "POST"])
def add_shipment():
    message = None

    if request.method == "POST":
        #Package data
        customer_id = request.form["customer_id"]
        weight = request.form["weight"]
        length = request.form["length"]
        width = request.form["width"]
        height = request.form["height"]
        declared_value = request.form["value"]
        special_cargo = request.form["special"]
        #Shipment data
        employee_id = request.form["employee_id"]
        vehicle_id = request.form["vehicle_id"]
        delivery_location = request.form["location"]
        distance = request.form["distance"]
        expected_date = request.form["date"]
        
        conn = get_connection()
        cursor = conn.cursor()
        
        #Insert package
        cursor.execute("""
            INSERT INTO Package (customer_id, weight_lbs, length_in, width_in, height_in, declared_value, special_cargo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (customer_id, weight, length, width, height, declared_value, special_cargo))
        
        package_id = cursor.lastrowid
        
        # Insert shipment
        cursor.execute("""
            INSERT INTO Shipment (package_id, employee_id, vehicle_id, delivery_location, distance_miles, status, expected_delivery_date)
            VALUES (?, ?, ?, ?, ?, 'Pending', ?)
        """, (package_id, employee_id, vehicle_id, delivery_location, distance, expected_date))
        
        conn.commit()
        
        message = "Shipment created successfully!"
        
        cursor.close()
        conn.close()

    return render_template("add_shipment.html", message=message)


 
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



 
# RUN THE APP
 
if __name__ == "__main__":
    app.run(debug=True)