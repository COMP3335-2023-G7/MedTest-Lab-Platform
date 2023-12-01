from flask import Blueprint, request, jsonify
from helpers import contains_sqli_attempt, record_malicious_attempt, create_db_connection
import base64

results_bp = Blueprint('results_bp', __name__)

@results_bp.route('/api/results', methods=['POST'])
def submit_result():
    # try:
        data = request.form
        # Extracting fields from the request body
        order_id = data.get('orderId')
        interpretation = data.get('interpretation')
        reporting_pathologist = data.get('reportingPathologist')

        # Check for SQL Injection attempts and validate input
        if any(contains_sqli_attempt(x) for x in [order_id, interpretation, reporting_pathologist]):
            ip = request.remote_addr
            record_malicious_attempt(ip, "SQL Injection attempt in submit_result")
            return jsonify({'code': 400, 'message': 'Bad Request - Suspicious input detected.'}), 400

        if not all([order_id, interpretation, reporting_pathologist]):
            return jsonify({'code': 400, 'message': 'Bad Request - Missing or invalid input parameters.'}), 400

        # Database operation to insert the new result
        db = create_db_connection()

        with db.cursor() as cursor:
            query = """
                INSERT INTO Results (ORDER_ID, INTERPRETATION, REPORTING_PATHOLOGIST)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (order_id, interpretation, reporting_pathologist))
            db.commit()
            result_id = cursor.lastrowid

            return jsonify({'code': 201, 'message': 'Result submitted successfully.', 'data': {'resultId': result_id}}), 201
        
    # except Exception as e:
    #     return jsonify({'code': 500, 'message': 'Internal Server Error - ' + str(e)}), 500


@results_bp.route('/api/results', methods=['GET'])
def get_results():
    # try:
        result_id = request.args.get('resultId')
        order_id = request.args.get('orderId')
        patient_id = request.args.get('patientId')

        # Check for SQL Injection attempts
        # Note: Implement contains_sqli_attempt() to check for SQL injection
        suspicious_inputs = [x for x in [result_id, order_id, patient_id] if x is not None]
        if any(contains_sqli_attempt(x) for x in suspicious_inputs):
            ip = request.remote_addr
            record_malicious_attempt(ip, "SQL Injection attempt in get_results")
            return jsonify({'code': 400, 'message': 'Bad Request - Suspicious input detected.'}), 400

        db = create_db_connection()  # Ensure create_db_connection() is defined to connect to your database
        with db.cursor() as cursor:
            if result_id and not order_id and not patient_id:
                cursor.execute("""
                    SELECT *, 
                        REPORT_URL, 
                        INTERPRETATION,
                        REPORTING_PATHOLOGIST
                    FROM Results
                    WHERE RESULT_ID = %s
                """, (result_id))
                results = cursor.fetchall()
                print(results)
                return jsonify({'code': 200, 'message': 'Result retrieved successfully.', 'data': results}), 200

            elif order_id and not result_id and not patient_id:
                cursor.execute("""
                    SELECT
                        REPORT_URL, 
                        INTERPRETATION,
                        REPORTING_PATHOLOGIST
                    FROM Results
                    WHERE ORDER_ID = %s
                """, (order_id))
                results = cursor.fetchone()
                cursor.execute("""
                    SELECT TEST_CODE, ORDER_DATE FROM Orders WHERE ORDER_ID = %s
                """, (order_id))
                orderInfo = cursor.fetchone()
                test_code = orderInfo['TEST_CODE']
                order_date = orderInfo['ORDER_DATE']
                cursor.execute("""
                    SELECT NAME FROM TestsCatalog WHERE TEST_CODE = %s
                """, (test_code))
                testName = cursor.fetchone()
                testName = testName['NAME']
                info = {
                    "testName": testName,
                    "orderDate": order_date,
                    "testCode": test_code,
                    "REPORT_URL": results['REPORT_URL'],
                    "INTERPRETATION": results['INTERPRETATION'],
                    "REPORTING_PATHOLOGIST": results['REPORTING_PATHOLOGIST']
                }

                return jsonify({'code': 200, 'message': 'Result retrieved successfully.', 'data': info}), 200

            elif patient_id and not result_id and not order_id:
                cursor.execute("""
                    SELECT
                        REPORT_URL, 
                        INTERPRETATION,
                        REPORTING_PATHOLOGIST
                    FROM Results
                    WHERE ORDER_ID IN (
                        SELECT ORDER_ID FROM Appointments WHERE PATIENT_ID = %s
                    )
                """, (patient_id))
                results = cursor.fetchone()
                cursor.execute("""
                    SELECT TEST_CODE, ORDER_DATE FROM Orders WHERE PATIENT_ID = %s
                """, (patient_id))
                orderInfo = cursor.fetchone()
                test_code = orderInfo['TEST_CODE']
                order_date = orderInfo['ORDER_DATE']
                cursor.execute("""
                    SELECT NAME FROM TestsCatalog WHERE TEST_CODE = %s
                """, (test_code))
                testName = cursor.fetchone()
                testName = testName['NAME']
                info = {
                    "testName": testName,
                    "orderDate": order_date,
                    "testCode": test_code,
                    "REPORT_URL": results['REPORT_URL'],
                    "INTERPRETATION": results['INTERPRETATION'],
                    "REPORTING_PATHOLOGIST": results['REPORTING_PATHOLOGIST']
                }

                return jsonify({'code': 200, 'message': 'Result retrieved successfully.', 'data': info}), 200

    # except Exception as e:
    #     return jsonify({'code': 500, 'message': 'Internal Server Error - ' + str(e)}), 500




