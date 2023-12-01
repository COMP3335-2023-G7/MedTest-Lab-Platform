import os
from datetime import datetime
import pymysql
import hashlib
import config
from flask import request
import jwt
import base64

SQLI_BLACKLIST = ["'", '"', ";", "--", "/*", "*/", "=", "%"]

def contains_sqli_attempt(input_string):
    return any(char in input_string for char in SQLI_BLACKLIST)

def record_malicious_attempt(ip, details):
    path = os.path.join(os.getcwd(), "log.txt")
    with open(path, "a") as file:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Time: {current_time}, IP: {ip}, Details: {details}\n")

def generate_salt():
    return os.urandom(16).hex()

def generate_session_key():
    return os.urandom(24)

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def create_db_connection():
    """Just for demo purposes."""
    return pymysql.connect(host=config.MYSQL_HOST,
                           user=config.MYSQL_USER,
                           password=config.MYSQL_PASSWORD,
                           db=config.MYSQL_DB,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

def verify_token(token):
    try:
        decoded = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return False
    except jwt.InvalidTokenError:
        print("Invalid token")
        return False

    # Extract identity and session_key
    identity = decoded.get('sub')
    session_key = decoded.get('session_key')

    if not identity or not session_key:
        print("Missing identity or session key in token")
        return False
    
    # Verify with database
    connection = create_db_connection()
    if connection is None:
        print("Failed to create database connection")
        return False

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Patients WHERE NAME = %s AND SESSION_KEY = %s", (identity, session_key))
            result = cursor.fetchone()
            return bool(result)
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return False
    finally:
        connection.close()

def mysql_aes_encrypt(data, key, connection):
    with connection.cursor() as cursor:
        query = "SELECT HEX(AES_ENCRYPT(%s, UNHEX(%s))) AS encrypted"
        cursor.execute(query, (data, key))
        result = cursor.fetchone()
        return result['encrypted'] if result else None

def mysql_aes_decrypt(encrypted_data, key, connection):
    with connection.cursor() as cursor:
        query = "SELECT AES_DECRYPT(UNHEX(%s), UNHEX(%s)) AS decrypted"
        cursor.execute(query, (encrypted_data, key))
        result = cursor.fetchone()
        return result['decrypted'].decode('utf-8') if result and result['decrypted'] else None

def mysql_random_bytes(length, connection):
    with connection.cursor() as cursor:
        query = "SELECT HEX(RANDOM_BYTES(%s)) AS random_bytes"
        cursor.execute(query, (length,))
        result = cursor.fetchone()
        return result['random_bytes'] if result else None
