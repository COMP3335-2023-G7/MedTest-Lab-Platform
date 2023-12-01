from flask import Blueprint, jsonify, request
from helpers import contains_sqli_attempt, record_malicious_attempt, create_db_connection, verify_token
from patient_routes import getPatientById

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/api/appointments', methods=['GET'])
def get_all_appointments():

    accessToken = request.cookies.get('access_token')
    if verify_token(accessToken):
        query = "SELECT * FROM Appointments"
        connection = create_db_connection()

        try:
            with connection.cursor() as cursor:

                cursor.execute(query)
                result = cursor.fetchall()

                appointments = []
                for row in result:

                    sql = "SELECT SALT FROM Patients WHERE PATIENT_ID = %s"
                    cursor.execute(sql, (row["PATIENT_ID"],))
                    salt = cursor.fetchone()
                    salt = salt['SALT']

                    info = getPatientById(row["PATIENT_ID"])

                    sql = "SELECT NAME FROM TestsCatalog WHERE TEST_CODE = %s"
                    cursor.execute(sql, (row["TESTCODE"],))
                    testName = cursor.fetchone()
                    testName = testName['NAME']
                    finallResult = {
                        "patientId": row["PATIENT_ID"],
                        "date": row["DATETIME"],
                        "test_code": row["TESTCODE"],
                        "name": info["name"],
                        "contact": info["contact"],
                        "INSURANCE_DETAILS": info["insurance_details"],
                        "testName": testName
                    }
                    appointments.append(finallResult)
                    

        finally:
            connection.close()

        return jsonify({
            "code": 200,
            "message": "Appointments retrieved successfully.",
            "data": appointments
        })

    else:
        return jsonify({
            "code": 401,
            "message": "Unauthorized - Invalid access token."
        }), 401


@appointment_bp.route('/api/appointments', methods=['POST'])
def create_appointment():
    accessToken = request.cookies.get('access_token')
    if verify_token(accessToken):

        data = request.form
        # Validate required fields
        required_fields = ['patientId', 'date', 'test_code']
        if not all(field in data for field in required_fields):
            return jsonify({
                "code": 400,
                "message": "Bad Request - Missing or invalid input parameters."
            }), 400

        connection = create_db_connection()
        try:
            with connection.cursor() as cursor:

                query = "INSERT INTO Appointments (PATIENT_ID, DATETIME, TESTCODE) VALUES (%s, %s, %s)"
                values = (data["patientId"], data["date"], data["test_code"])
                cursor.execute(query, values)
                connection.commit()

        finally:
            connection.close()

        return jsonify({
            "code": 201,
            "message": "Appointment created successfully.",
        }), 201

    else:
        return jsonify({
            "code": 401,
            "message": "Unauthorized - Invalid access token."
        }), 401


@appointment_bp.route('/api/appointments', methods=['GET'])
def get_appointments_by_patient_id():

    accessToken = request.cookies.get('access_token')
    if verify_token(accessToken):

        patientId = request.args.get('patientId')
        if not patientId:
            return jsonify({
                "code": 400,
                "message": "Bad Request - Invalid patientId parameter."
            }), 400

        query = "SELECT * FROM Appointments WHERE patientId = %s"
        values = (patientId,)
        connection = create_db_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                result = cursor.fetchall()

            if result:
                appointments = []
                for row in result:
                    appointment = {
                        "patientId": row["PATIENT_ID"],
                        "date": row["DATETIME"],
                        "test_code": row["TESTCODE"],
                    }
                    appointments.append(appointment)
                    sql = "SELECT SALT FROM Patients WHERE PATIENT_ID = %s"
                    cursor.execute(sql, (row["PATIENT_ID"],))
                    salt = cursor.fetchone()
                    salt = salt['SALT']

                    sql = "SELECT AES_DECRYPT(NAME, %s) AS NAME, AES_DECRYPT(CONTACT, %s) AS CONTACT, AES_DECRYPT(INSURANCE_DETAILS, %s) AS INSURANCE_DETAILS FROM Patients WHERE PATIENT_ID = %s"
                    cursor.execute(sql, (salt, salt, salt, row["PATIENT_ID"]))
                    patient = cursor.fetchone()
                    info = {
                        "name": patient["NAME"].decode('utf-8'),
                        "contact": patient["CONTACT"].decode('utf-8'),
                        "INSURANCE_DETAILS": patient["INSURANCE_DETAILS"].decode('utf-8')
                    }
                    appointments.append(info)

                    sql = "SELECT NAME FROM TestsCatalog WHERE TEST_CODE = %s"
                    cursor.execute(sql, (row["TESTCODE"],))
                    testName = cursor.fetchone()
                    testName = testName['NAME']
                    test = {
                        "testName": testName
                    }
                    appointments.append(test)

                return jsonify({
                    "code": 200,
                    "message": "Appointments for the patient retrieved successfully.",
                    "data": appointments
                })
        finally:
            connection.close()

        return jsonify({
            "code": 404, "message": "Not Found - No appointments found for the given patient ID."
        }), 404

    else:
        return jsonify({
            "code": 401,
            "message": "Unauthorized - Invalid access token."
        }), 401


@appointment_bp.route('/api/appointments/<appointmentId>', methods=['PUT'])
def update_appointment(appointmentId):
    data = request.form()
    accessToken = request.cookies.get('access_token')
    if verify_token(accessToken):

        query = "UPDATE Appointments SET date = %s WHERE appointmentId = %s"
        values = (data["date"], appointmentId)

        connection = create_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                connection.commit()

        finally:
            connection.close()

        return jsonify({
            "code": 200,
            "message": "Appointment updated successfully."
        }), 200

    else:
        return jsonify({
            "code": 401,
            "message": "Unauthorized - Invalid access token."
        }), 401



@appointment_bp.route('/api/appointments/<appointmentId>', methods=['DELETE'])
def delete_appointment(appointmentId):
    accessToken = request.cookies.get('access_token')
    if verify_token(accessToken):

        query = "DELETE FROM Appointments WHERE appointmentId = %s"
        values = (appointmentId,)

        connection = create_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, values)
                connection.commit()

        finally:
            connection.close()

        return jsonify({
            "code": 200,
            "message": "Appointment deleted successfully."
        }), 200

    return jsonify({
        "code": 401,
        "message": "Unauthorized - Invalid access token."
    }), 401
