from flask import Flask, request, jsonify, Blueprint
from helpers import contains_sqli_attempt, record_malicious_attempt, create_db_connection, verify_token

test_bp = Blueprint('test_bp', __name__)

@test_bp.route('/api/tests', methods=['POST'])
def create_test():
    """
    Create a new test.

    This endpoint allows the creation of a new test by providing the test name, description, and cost in the request body.

    Returns:
        A JSON response containing the status code, message, and the test ID if the test is created successfully.
    """
    accessToken = request.cookies.get('access_token')
    if verify_token(accessToken):
        try:
            data = request.form
            name = data.get('name')
            description = data.get('description')
            cost = data.get('cost')

            # Check for SQL Injection attempts
            if any(contains_sqli_attempt(x) for x in [name, description, str(cost)]):
                ip = request.remote_addr
                record_malicious_attempt(ip, "SQL Injection attempt in create_test")
                return jsonify({'code': 400, 'message': 'Bad Request - Suspicious input detected.'}), 400

            # Validate input parameters
            if not all([name, description, cost]):
                return jsonify({'code': 400, 'message': 'Bad Request - Missing or invalid input parameters.'}), 400

            db = create_db_connection()
            with db.cursor() as cursor:
                query = "INSERT INTO TestsCatalog (name, description, cost) VALUES (%s, %s, %s)"
                cursor.execute(query, (name, description, cost))
                db.commit()
                test_id = cursor.lastrowid  # Assuming test_code is auto-incremented

            return jsonify({'code': 201, 'message': 'Test created successfully.', 'data': {'testId': test_id}}), 201
        except Exception as e:
            return jsonify({'code': 500, 'message': 'Internal Server Error - ' + str(e)}), 500

    return jsonify({
        "code": 401,
        "message": "Unauthorized - Invalid access token."
    }), 401

# @test_bp.route('/api/tests', methods=['PUT'])
# def update_test():
#     """
#     Update an existing test.

#     This endpoint allows the update of an existing test by providing the test ID, along with the updated test name, description, and cost in the request body.

#     Returns:
#         A JSON response containing the status code and message if the test is updated successfully.
#     """
#     try:
#         test_id = request.args.get('testId')
#         data = request.json
#         name = data.get('name')
#         description = data.get('description')
#         cost = data.get('cost')

#         # Check for SQL Injection attempts
#         if any(contains_sqli_attempt(x) for x in [test_id, name, description, str(cost)]):
#             ip = request.remote_addr
#             record_malicious_attempt(ip, "SQL Injection attempt in update_test")
#             return jsonify({'code': 400, 'message': 'Bad Request - Suspicious input detected.'}), 400

#         # Validate input parameters
#         if not all([test_id, name, description, cost]):
#             return jsonify({'code': 400, 'message': 'Bad Request - Missing or invalid input parameters.'}), 400

#         db = create_db_connection()
#         with db.cursor() as cursor:
#             query = "UPDATE TestsCatalog SET name=%s, description=%s, cost=%s WHERE test_code=%s"
#             cursor.execute(query, (name, description, cost, test_id))
#             db.commit()

#         return jsonify({'code': 200, 'message': 'Test updated successfully.'}), 200
#     except Exception as e:
#         return jsonify({'code': 500, 'message': 'Internal Server Error - ' + str(e)}), 500
    
@test_bp.route('/api/tests', methods=['GET'])
def get_tests():
    """
    Retrieve tests from the catalog.

    This endpoint allows the retrieval of tests from the catalog. It can either retrieve all tests or a specific test by providing a test ID.

    Returns:
        A JSON response containing the status code, message, and an array of test objects.
    """
    # accessToken = request.cookies.get('access_token')
    # if verify_token(accessToken):
    try:
        test_id = request.args.get('testId')
        db = create_db_connection()

        with db.cursor() as cursor:
            if test_id:
                # Validate test_id to prevent SQL Injection
                if contains_sqli_attempt(test_id):
                    ip = request.remote_addr
                    record_malicious_attempt(ip, "SQL Injection attempt in get_tests")
                    return jsonify({'code': 400, 'message': 'Bad Request - Suspicious input detected.'}), 400

                query = "SELECT * FROM TestsCatalog WHERE test_code = %s"
                cursor.execute(query, (test_id,))
            else:
                query = "SELECT * FROM TestsCatalog"
                cursor.execute(query)

            result = cursor.fetchall()
            tests = []
            for row in result:
                test = {
                    'testId': row['TEST_CODE'],
                    'name': row.get('NAME', 'N/A'),
                    'description': row.get('DESCRIPTION', 'N/A'),
                    'cost': row.get('COST', 'N/A')
                }
                tests.append(test)

        return jsonify({'code': 200, 'message': 'Tests retrieved successfully.', 'data': tests}), 200
    except Exception as e:
        return jsonify({'code': 500, 'message': 'Internal Server Error - ' + str(e)}), 500

    # return jsonify({
    #         "code": 401,
    #         "message": "Unauthorized - Invalid access token."
    #     }), 401



if __name__ == '__main__':
    test_bp.run(debug=True)
