from flask import Blueprint, jsonify, request
from helpers import contains_sqli_attempt, record_malicious_attempt, create_db_connection, verify_token
from patient_routes import getPatientById

order_bp = Blueprint('order', __name__)

@order_bp.route('/api/orders', methods=['GET'])
def get_order():
    accessToken = request.cookies.get('access_token')
    if (verify_token(accessToken)):
    
        order_id = request.args.get('orderId')
        # input validation
        if not order_id:
            query = "SELECT * FROM Orders"
            connection = create_db_connection()
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    result = cursor.fetchall()

            finally:
                connection.close()

            orders = []
            for row in result:
                patientInfo = getPatientById(row["PATIENT_ID"])
                order = {
                    "orderId": row["ORDER_ID"],
                    "patientId": row["PATIENT_ID"],
                    "testCode": row["TEST_CODE"],
                    "orderingPhysician": row["ORDERING_PHYSICIAN"],
                    "orderDate": row["ORDER_DATE"],
                    "status": row["STATUS"],
                    "patientName": patientInfo["name"],
                    "patientBirthdate": patientInfo["birthdate"],
                    "patientContact": patientInfo["contact"]
                }
                orders.append(order)
                print(orders)

            return jsonify({
                "code": 200,
                "message": "Orders retrieved successfully.",
                "data": orders
            })

        if contains_sqli_attempt(order_id):
            ip_address = request.remote_addr
            record_malicious_attempt(ip_address, f"SQL injection attempt: {order_id}")
            return jsonify({
                "code": 400,
                "message": "Bad Request - Invalid orderId parameter."
            }), 400

        query = "SELECT * FROM Orders WHERE ORDER_ID = %s"
        values = (order_id,)

        connection = create_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                result = cursor.fetchone()

        finally:
            connection.close()

        if result:
            order = {
                "orderId": result[0],
                "appointmentId": result[1],
                "testCode": result[2],
                "patientId": result[3],
                "orderStatus": result[4],
                "details": result[5]
            }

            return jsonify({
                "code": 200,
                "message": "Order retrieved successfully.",
                "data": order
            })

        return jsonify({
            "code": 404,
            "message": "Not Found - The specified order does not exist."
        }), 404
    else:
        return jsonify({
            "code": 401,
            "message": "Unauthorized - Invalid access token."
        }), 401


@order_bp.route('/api/orders', methods=['GET'])
def get_orders_by_patient_id():
    patient_id = request.args.get('patientId')

    # Input validation
    if not patient_id:
        return jsonify({
            "code": 400,
            "message": "Bad Request - Missing patientId parameter."
        }), 400

    if contains_sqli_attempt(patient_id):
        ip_address = request.remote_addr
        record_malicious_attempt(ip_address, f"SQL injection attempt: {patient_id}")
        return jsonify({
            "code": 400,
            "message": "Bad Request - Invalid patientId parameter."
        }), 400

    query = "SELECT * FROM Orders WHERE PATIENT_ID = %s"
    values = (patient_id,)

    connection = create_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchall()

    finally:
        connection.close()

    if result:
        orders = []
        for row in result:
            order = {
                "orderId": row[0],
                "patientId": row[1],
                "testCode": row[2],
                "orderingPhysician": row[3],
                "orderDate": row[4],
                "status": row[5]
            }
            orders.append(order)

        return jsonify({
            "code": 200,
            "message": "Orders retrieved successfully.",
            "data": orders
        })

    return jsonify({
        "code": 404,
        "message": "Not Found - No orders found for the specified patient ID."
    }), 404


# @order_bp.route('/api/orders', methods=['GET'])
# def get_all_order():
#     query = "SELECT * FROM Orders"
#     connection = create_db_connection()
#     try:
#         with connection.cursor() as cursor:
#             cursor.execute(query)
#             result = cursor.fetchall()

#     finally:
#         connection.close()

#     orders = []
#     for row in result:
#         order = {
#             "orderId": row[0],
#             "patientId": row[1],
#             "testCode": row[2],
#             "orderingPhysician": row[3],
#             "orderDate": row[4],
#             "status": row[5]
#         }
#         orders.append(order)

#     return jsonify({
#         "code": 200,
#         "message": "Orders retrieved successfully.",
#         "data": orders
#     })

# Endpoint to create a new order
@order_bp.route('/api/orders', methods=['POST'])
def create_order():
    data = request.form
    # Validate required fields
    required_fields = ['testCode', 'patientId', 'orderingPhysician', 'orderStatus']
    if not all(field in data for field in required_fields):
        return jsonify({
            "code": 400,
            "message": "Bad Request - Missing or invalid input parameters."
        }), 400

    connection = create_db_connection()

    getAppointmentIdQuery = "SELECT APPOINTMENT_ID FROM Appointments WHERE TESTCODE = %s AND PATIENT_ID = %s"
    getAppointmentIdValues = (data.get("testCode"), data.get("patientId"))

    # Check if an order for this appointment already exists
    

    try:
        with connection.cursor() as cursor:
            # Get the appointment ID
            cursor.execute(getAppointmentIdQuery, getAppointmentIdValues)
            appointment_id = cursor.fetchone()
            print(appointment_id["APPOINTMENT_ID"])
            query = "SELECT * FROM Orders WHERE APPOINTMENT_ID = %s"
            values = (appointment_id["APPOINTMENT_ID"])
            cursor.execute(query, values)
            existing_order = cursor.fetchone()

            if existing_order:
                return jsonify({
                    "code": 409,
                    "message": "Conflict - An order for this appointment already exists."
                }), 409

            # Create the new order
            query = "INSERT INTO Orders (PATIENT_ID, APPOINTMENT_ID, TEST_CODE, ORDERING_PHYSICIAN, STATUS) VALUES (%s, %s, %s, %s, %s)"
            values = (data.get("patientId"), appointment_id["APPOINTMENT_ID"], data.get("testCode"), data.get("orderingPhysician"), data.get("orderStatus"))
            cursor.execute(query, values)
            connection.commit()
            new_order_id = cursor.lastrowid
        connection.commit()
        
    finally:
        connection.close()

    return jsonify({
        "code": 201,
        "message": "Order created successfully.",
        "data": {
            "orderId": new_order_id
        }
    }), 201
