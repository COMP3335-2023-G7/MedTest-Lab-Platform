from flask import Blueprint, jsonify, request
from helpers import contains_sqli_attempt, record_malicious_attempt, create_db_connection
import hashlib
import time
import os

billing_bp = Blueprint('billing', __name__)


@billing_bp.route('/api/bills', methods=['GET'])
def get_bill():
    order_id = request.args.get('orderId')
    # validate the input
    if not order_id or contains_sqli_attempt(order_id):
        record_malicious_attempt(request.remote_addr, f"SQL injection attempt: {order_id}")
        return jsonify({'error': 'Invalid billingId parameter'}), 400

    connection = create_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT * FROM Billing WHERE ORDER_ID = %s"
            cursor.execute(query, (order_id,))
            bill = cursor.fetchone()

            if bill:
                return jsonify(bill)

    finally:
        connection.close()

    return jsonify({'error': 'Bill not found'}), 404


@billing_bp.route('/api/bills', methods=['POST'])
def create_bill():
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

    return jsonify({'billingId': billing_id}), 201


@billing_bp.route('/api/bills', methods=['PUT'])
def update_bill():
    billing_id = request.args.get('billingId')
    if not billing_id or contains_sqli_attempt(billing_id):
        client_ip = request.remote_addr
        record_malicious_attempt(client_ip,
                                 f"SQL Injection attempt in billing update with Id: {billing_id}")
        return jsonify({'error': 'Invalid billingId parameter'}), 400

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing request body'}), 400

    connection = create_db_connection()
    try:
        with connection.cursor() as cursor:
            query = "UPDATE Billing SET ORDER_ID = %s, BILLED_AMOUNT = %s, PAYMENT_STATUS = %s, " \
                    "INSURANCE_CLAIM_STATUS = %s WHERE BILLING_ID = %s"
            values = (data.get('orderId'), data.get('billedAmount'), data.get('paymentStatus'),
                      data.get('insuranceClaimStatus'), billing_id)

            cursor.execute(query, values)
            connection.commit()

            # Check if we have updated any row.
            if cursor.rowcount > 0:
                return jsonify({'message': 'Bill updated successfully'})
    finally:
        connection.close()

    return jsonify({'error': 'Bill not found'}), 404

