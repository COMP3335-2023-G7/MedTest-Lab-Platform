from flask import Blueprint, jsonify, request
from helpers import contains_sqli_attempt, record_malicious_attempt, create_db_connection, verify_token
from patient_routes import getPatientById
import hashlib
import time
import os

billing_bp = Blueprint('billing', __name__)


@billing_bp.route('/api/bills', methods=['GET'])
def get_bill():
    accessToken = request.cookies.get('access_token')
    if verify_token(accessToken):
        patient_id = request.args.get('patientId')

        if patient_id:
            if contains_sqli_attempt(patient_id):
                record_malicious_attempt(request.remote_addr, f"SQL injection attempt: {patient_id}")
                return jsonify({'error': 'Invalid billingId parameter'}), 400

            connection = create_db_connection()
            if patient_id:
                try:
                    bill = []
                    with connection.cursor() as cursor:
                        query = "SELECT * FROM Orders WHERE PATIENT_ID = %s"
                        cursor.execute(query, (patient_id, ))
                        orderInfo = cursor.fetchall()

                        for row in orderInfo:
                            query = "SELECT PATIENT_ID FROM Orders WHERE ORDER_ID = %s"
                            cursor.execute(query, (row["ORDER_ID"],))
                            patient_id = cursor.fetchone()

                            query = "SELECT NAME FROM TestsCatalog WHERE TEST_CODE = %s"
                            cursor.execute(query, (row["TEST_CODE"],))
                            testName = cursor.fetchone()

                            query = "SELECT * FROM Billing WHERE ORDER_ID = %s"
                            cursor.execute(query, (row["ORDER_ID"],))
                            billInfo = cursor.fetchone()
                            if billInfo is not None:
                                patient = getPatientById(patient_id["PATIENT_ID"])

                                rowResult = {
                                    "billingId": billInfo["BILLING_ID"],
                                    "orderId": billInfo["ORDER_ID"],
                                    "billedAmount": billInfo["BILLED_AMOUNT"],
                                    "paymentStatus": billInfo["PAYMENT_STATUS"],
                                    "insuranceClaimStatus": billInfo["INSURANCE_CLAIM_STATUS"],
                                    "patientName": patient["name"],
                                    "patientContact": patient["contact"],
                                    "TestName": testName["NAME"],
                                    "TestCode": row["TEST_CODE"],
                                }
                                bill.append(rowResult)

                        if bill:
                            return jsonify({"message": "Bills retrieved successfully.", "data": bill})

                finally:
                    connection.close()

        if not patient_id:
            connection = create_db_connection()
            try:
                bill = []
                with connection.cursor() as cursor:
                    query = "SELECT * FROM Billing"
                    cursor.execute(query, ())
                    billQueryRes = cursor.fetchall()

                    for row in billQueryRes:
                        query = "SELECT PATIENT_ID FROM Orders WHERE ORDER_ID = %s"
                        cursor.execute(query, (row["ORDER_ID"],))
                        patient_id = cursor.fetchone()

                        patient = getPatientById(patient_id["PATIENT_ID"])

                        rowResult = {
                            "billingId": row["BILLING_ID"],
                            "orderId": row["ORDER_ID"],
                            "billedAmount": row["BILLED_AMOUNT"],
                            "paymentStatus": row["PAYMENT_STATUS"],
                            "insuranceClaimStatus": row["INSURANCE_CLAIM_STATUS"],
                            "patientName": patient["name"],
                            "patientContact": patient["contact"]
                        }
                        print(rowResult)
                        bill.append(rowResult)

                    if bill:
                        return jsonify({"message": "Bills retrieved successfully.", "data": bill})

            finally:
                connection.close()

        return jsonify({'error': 'Bill not found'}), 404

    return jsonify({
        "code": 401,
        "message": "Unauthorized - Invalid access token."
    }), 401


@billing_bp.route('/api/bills', methods=['POST'])
def create_bill():
    accessToken = request.cookies.get('access_token')
    if verify_token(accessToken):
        data = request.form
        required_fields = ['orderId', 'paymentStatus']

        if not data:
            return jsonify({'error': 'Missing request body'}), 400

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        connection = create_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = "SELECT TEST_CODE FROM Orders WHERE ORDER_ID = %s"
                cursor.execute(sql, (data['orderId'],))
                testCode = cursor.fetchone()
                test_code = testCode['TEST_CODE']

                sql = "SELECT COST FROM TestsCatalog WHERE TEST_CODE = %s"
                cursor.execute(sql, (test_code,))
                cost = cursor.fetchone()
                billedAmount = cost['COST']

                query = """
                    INSERT INTO Billing (ORDER_ID, BILLED_AMOUNT, PAYMENT_STATUS, INSURANCE_CLAIM_STATUS) 
                    VALUES (%s, %s, %s, %s)
                """
                values = (
                    data['orderId'],
                    billedAmount,
                    data['paymentStatus'],
                    data.get('insuranceClaimStatus', '')
                )
                cursor.execute(query, values)
                billing_id = cursor.lastrowid
                connection.commit()
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            connection.close()

        return jsonify({"message": "Bill created successfully.", 'billingId': billing_id}), 201

    return jsonify({
        "code": 401,
        "message": "Unauthorized - Invalid access token."
    }), 401

@billing_bp.route('/api/bills', methods=['PUT'])
def update_bill():
    accessToken = request.cookies.get('access_token')
    if verify_token(accessToken):
        billing_id = request.form.get('billingId')
        paymentStatus = request.form.get('paymentStatus')
        insuranceClaimStatus = request.form.get('insuranceClaimStatus')

        if not billing_id or contains_sqli_attempt(billing_id):
            client_ip = request.remote_addr
            record_malicious_attempt(client_ip,
                                     f"SQL Injection attempt in billing update with Id: {billing_id}")
            return jsonify({'error': 'Invalid billingId parameter'}), 400

        data = request.form
        if not data:
            return jsonify({'error': 'Missing request body'}), 400

        connection = create_db_connection()
        try:
            with connection.cursor() as cursor:
                query = "UPDATE Billing SET PAYMENT_STATUS = %s, INSURANCE_CLAIM_STATUS = %s WHERE BILLING_ID = %s"
                values = (paymentStatus,
                          insuranceClaimStatus, billing_id)

                cursor.execute(query, values)
                connection.commit()

                # Check if we have updated any row.
                if cursor.rowcount > 0:
                    return jsonify({'message': 'Bill updated successfully'})
        finally:
            connection.close()

        return jsonify({'error': 'Bill not found'}), 404

    return jsonify({
        "code": 401,
        "message": "Unauthorized - Invalid access token."
    }), 401




