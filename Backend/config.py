'''
Please config this file as per your own settings,
and you are not supposed to commit it to the repository.

Configuration file which is used to store configuration
settings or constants that are used throughout an application.
'''
MYSQL_HOST = 'db'  # or the name of your MySQL Docker service
MYSQL_USER = 'root'         # Default user
MYSQL_PASSWORD = 'root'     # Default password
MYSQL_DB = 'MedTest'        # Default database name
JWT_SECRET_KEY='medtest'     # Secret key for JWT
AES_SECRET_KEY='B374A26A71490437AA024E4FADD5B497FDFF1A8EA6FF12F6FB65AF2720B59CCF'     # Secret key for AES