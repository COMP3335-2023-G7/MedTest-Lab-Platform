from flask import Blueprint, request, jsonify, make_response
from helpers import contains_sqli_attempt, record_malicious_attempt, generate_salt, hash_password, create_db_connection, generate_session_key
import base64
from datetime import timedelta
from flask_jwt_extended import create_access_token

staff_bp = Blueprint('staff', __name__)

ALLOWED_USER_TYPES = {'patient', 'staff'}

@staff_bp.route('/api/login/staff', methods=['POST'])
def login_staff():
    data = request.form
    name = data.get('name')
    password = data.get('password')
    user_type = data.get('userType')

    if user_type not in ALLOWED_USER_TYPES:
        return jsonify({"error": "Invalid user type"}), 400

    if not all([name, password]):
        return jsonify({"message": "Bad Request - Missing or invalid input parameters."}), 400

    if contains_sqli_attempt(name) or contains_sqli_attempt(password):
        client_ip = request.remote_addr
        record_malicious_attempt(client_ip, f"SQL Injection attempt in staff login with Name: {name}, Password: [FILTERED]")
        return jsonify({"error": "Invalid input detected"}), 400

    connection = create_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT PASSWORD, SALT, ROLE FROM Staff WHERE NAME = %s", (name,))
            result = cursor.fetchone()
            print(result)
            # Check if staff member exists and verify the password
            if result:
                stored_hashed_password, salt = result['PASSWORD'], result['SALT']
                salt = salt
                if stored_hashed_password.decode('utf-8') == hash_password(password, salt):
                    session_key = generate_session_key()
                    ## add the identity and session key to create_access_token
                    encoded_session_key = base64.b64encode(session_key).decode('utf-8')
                    if (result["ROLE"] == "Lab Staff"):
                        user_type = "labstaff"
                    elif (result["ROLE"] == "Secretary"):
                        user_type = "secretary"
                    access_token = create_access_token(identity=name, additional_claims={"session_key": encoded_session_key, "type": user_type}, expires_delta=timedelta(seconds=1800))
                    session_key = generate_session_key()
                    cursor.execute("UPDATE Staff SET SESSION_KEY = %s WHERE NAME = %s", (encoded_session_key, name))
                    connection.commit()
                    response = make_response(jsonify({"message": "Staff login successful.", "type": user_type}), 200)
                    response.set_cookie("access_token", access_token)
                    return response
                else:
                    # TODO: Modify the api document.
                    return jsonify({"message": "Invalid credentials."}), 401
    finally:
        connection.close()

    return jsonify({"message": "Internal Server Error"}), 500
