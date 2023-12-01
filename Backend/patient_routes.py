from flask import Blueprint, request, jsonify, make_response
from helpers import contains_sqli_attempt, record_malicious_attempt, generate_salt, hash_password, create_db_connection, generate_session_key
from flask_jwt_extended import create_access_token
import base64
from datetime import timedelta

patient_bp = Blueprint('patient', __name__)

ALLOWED_USER_TYPES = {'patient', 'staff'}

@patient_bp.route('/api/signup/patient', methods=['POST'])
def register_patient():
    data = request.form
    print(data)
    name = data.get('name')
    birthdate = data.get('birthday')
    contact = data.get('contact')
    insurance_details = data.get('insurance')
    password = data.get('password')
    print(name, birthdate, contact, insurance_details, password)
    if not all([name, birthdate, contact, insurance_details, password]):
        return jsonify({"message": "Bad Request - Missing or invalid input parameters."}), 400

    if any(contains_sqli_attempt(field) for field in [name, birthdate, contact, insurance_details, password]):
        client_ip = request.remote_addr
        record_malicious_attempt(client_ip,
                                 f"SQL Injection attempt in patient registration with Name: {name}, Birthdate: {birthdate}, Contact: {contact}, Insurance: {insurance_details}, Password: [FILTERED]")
        return jsonify({"error": "Invalid input detected"}), 400

    salt = generate_salt()
    hashed_password = hash_password(password, salt)
    connection = create_db_connection()
    try:
        with connection.cursor() as cursor:
            # Check if patient already exists
            cursor.execute("SELECT * FROM Patients WHERE NAME = %s", (name,))
            if cursor.fetchone():
                return jsonify({"message": "Conflict - Patient already exists."}), 409

            # Insert new patient
            sql = "INSERT INTO Patients (NAME, BIRTHDATE, CONTACT, INSURANCE_DETAILS, PASSWORD, SALT) VALUES (%s, AES_ENCRYPT(%s, %s), AES_ENCRYPT(%s, %s), AES_ENCRYPT(%s, %s), %s, %s)"
            cursor.execute(sql, (name, birthdate, salt, contact, salt, insurance_details, salt, hashed_password, salt))
            patient_id = cursor.lastrowid
        connection.commit()
    finally:
        connection.close()
    return jsonify({"message": "Patient created successfully.", "data": {"patientId": patient_id}}), 201

@patient_bp.route('/api/login/patient', methods=['POST'])
def login_patient():
    data = request.form
    name = data.get('name')
    user_type = data.get('userType')
    password = data.get('password')

    if user_type not in ALLOWED_USER_TYPES:
        return jsonify({"error": "Invalid user type"}), 400

    if not all([name, password]):
        return jsonify({"message": "Bad Request - Missing or invalid input parameters."}), 400

    if contains_sqli_attempt(name) or contains_sqli_attempt(password):
        client_ip = request.remote_addr
        record_malicious_attempt(client_ip, f"SQL Injection attempt in patient login with Name: {name}, Password: [FILTERED]")
        return jsonify({"error": "Invalid input detected"}), 400

    connection = create_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT PASSWORD, SALT, PATIENT_ID FROM Patients WHERE NAME = %s", (name,))
            result = cursor.fetchone()

            # Check if patient exists and verify the password
            if result:
                stored_hashed_password, salt = result['PASSWORD'], result['SALT']
                if stored_hashed_password.decode('utf-8') == hash_password(password, salt):
                    session_key = generate_session_key()
                    ## add the identity and session key to create_access_token
                    encoded_session_key = base64.b64encode(session_key).decode('utf-8')
                    access_token = create_access_token(identity=name, additional_claims={"session_key": encoded_session_key}, expires_delta=timedelta(seconds=1800))
                    cursor.execute("UPDATE Patients SET SESSION_KEY = %s WHERE NAME = %s", (encoded_session_key, name))
                    connection.commit()
                    response = make_response(jsonify({"message": "Patient login successful.", "patient_id": result["PATIENT_ID"]}), 200)
                    response.set_cookie("access_token", access_token)
                    return response
                else:
                    # this should align with there not exist such patient, just in case attacker enumerate users.
                    return jsonify({"message": "Invalid credentials."}), 401
    finally:
        connection.close()

    return jsonify({"message": "Internal Server Error"}), 500

@patient_bp.route('/api/patient', methods=['GET'])
def get_patient():
    patient_id = request.args.get('patientId')
    connection = create_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT SALT FROM Patients WHERE PATIENT_ID = %s", (patient_id,))
            result = cursor.fetchone()
            if result:
                salt = result['SALT']

                # Now, use the salt to decrypt the other fields
                cursor.execute("""
                    SELECT PATIENT_ID, NAME, 
                        AES_DECRYPT(BIRTHDATE, %s) as BIRTHDATE, 
                        AES_DECRYPT(CONTACT, %s) as CONTACT, 
                        AES_DECRYPT(INSURANCE_DETAILS, %s) as INSURANCE_DETAILS
                    FROM Patients 
                    WHERE PATIENT_ID = %s
                    """, (salt, salt, salt, patient_id))

                patient = cursor.fetchone()

                if patient:
                    patient_data = {
                        "patientId": patient['PATIENT_ID'],
                        "name": patient['NAME'],
                        "birthdate": patient['BIRTHDATE'].decode('utf-8') if patient['BIRTHDATE'] else None,
                        "contact": patient['CONTACT'].decode('utf-8') if patient['CONTACT'] else None,
                        "insurance_details": patient['INSURANCE_DETAILS'].decode('utf-8') if patient['INSURANCE_DETAILS'] else None
                    }
                    return jsonify({"message": "Patient found.", "data": patient_data}), 200
                else:
                    return jsonify({"message": "Patient not found."}), 404

    finally:
        connection.close()


def getPatientById(patient_id):
    connection = create_db_connection()

    with connection.cursor() as cursor:
        cursor.execute("SELECT SALT FROM Patients WHERE PATIENT_ID = %s", (patient_id,))
        result = cursor.fetchone()
        if result:
            salt = result['SALT']

            # Now, use the salt to decrypt the other fields
            cursor.execute("""
                SELECT PATIENT_ID, NAME, 
                    AES_DECRYPT(BIRTHDATE, %s) as BIRTHDATE, 
                    AES_DECRYPT(CONTACT, %s) as CONTACT, 
                    AES_DECRYPT(INSURANCE_DETAILS, %s) as INSURANCE_DETAILS
                FROM Patients 
                WHERE PATIENT_ID = %s
                """, (salt, salt, salt, patient_id))

            patient = cursor.fetchone()

            if patient:
                patient_data = {
                    "patientId": patient['PATIENT_ID'],
                    "name": patient['NAME'],
                    "birthdate": patient['BIRTHDATE'].decode('utf-8') if patient['BIRTHDATE'] else None,
                    "contact": patient['CONTACT'].decode('utf-8') if patient['CONTACT'] else None,
                    "insurance_details": patient['INSURANCE_DETAILS'].decode('utf-8') if patient['INSURANCE_DETAILS'] else None
                }
                return patient_data
        # else:
        #     patient_data = None
        #     return patient_data

