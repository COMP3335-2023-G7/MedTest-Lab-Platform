from flask import Flask
from patient_routes import patient_bp
from staff_routes import staff_bp
from billing_routes import billing_bp
from order_routes import order_bp
from result import results_bp
from test import test_bp
from appointment_routes import appointment_bp

from flask_cors import CORS, cross_origin

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

import config

# It's advisable to factor our app into a set of blueprints.
# instead of merely using one file which is hard to read

# TODO: SSL key function to implement.

app = Flask(__name__)

cors = CORS(app, supports_credentials=True, resources={
    r"/api/*": {
        "origins": "*"
    }
})

app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
jwt = JWTManager(app)

app.register_blueprint(patient_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(order_bp)
app.register_blueprint(results_bp)
app.register_blueprint(test_bp)
app.register_blueprint(appointment_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6688)
