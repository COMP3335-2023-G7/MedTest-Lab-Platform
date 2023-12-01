CREATE DATABASE MedTest;
USE MedTest;

CREATE TABLE Patients (
    PATIENT_ID INT PRIMARY KEY AUTO_INCREMENT,
    NAME VARCHAR(255) NOT NULL,
    BIRTHDATE VARBINARY(255) NOT NULL,
    CONTACT VARBINARY(255),
    INSURANCE_DETAILS VARBINARY(255),
    PASSWORD VARBINARY(255) NOT NULL,
    SALT VARCHAR(255) NOT NULL,
    SESSION_KEY VARCHAR(255)
);

CREATE TABLE TestsCatalog (
    TEST_CODE INT PRIMARY KEY AUTO_INCREMENT,
    NAME VARCHAR(255) NOT NULL,
    DESCRIPTION TEXT,
    COST DECIMAL(10,2) NOT NULL
);
CREATE TABLE Staff (
    STAFF_ID INT PRIMARY KEY AUTO_INCREMENT,
    NAME VARCHAR(255) NOT NULL,
    ROLE ENUM('Lab Staff', 'Secretary') NOT NULL,
    CONTACT VARBINARY(255),
    PASSWORD VARBINARY(255) NOT NULL,
    SALT VARCHAR(255) NOT NULL,
    SESSION_KEY VARCHAR(255)
);
CREATE TABLE Orders (
    ORDER_ID INT PRIMARY KEY AUTO_INCREMENT,
    PATIENT_ID INT NOT NULL,
    APPOINTMENT_ID INT NOT NULL,
    TEST_CODE INT NOT NULL,
    ORDERING_PHYSICIAN VARCHAR(255) NOT NULL,
    ORDER_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    STATUS VARCHAR(255) NOT NULL,
    FOREIGN KEY (PATIENT_ID) REFERENCES Patients(PATIENT_ID),
    FOREIGN KEY (TEST_CODE) REFERENCES TestsCatalog(TEST_CODE),
    FOREIGN KEY (APPOINTMENT_ID) REFERENCES Appointments(APPOINTMENT_ID)
);

CREATE TABLE Appointments (
    APPOINTMENT_ID INT PRIMARY KEY AUTO_INCREMENT,
    PATIENT_ID INT NOT NULL,
    TESTCODE INT NOT NULL,
    DATETIME DATETIME NOT NULL,
    FOREIGN KEY (PATIENT_ID) REFERENCES Patients(PATIENT_ID),
    FOREIGN KEY (TESTCODE) REFERENCES TestsCatalog(TEST_CODE)
);

CREATE TABLE Results (
    RESULT_ID INT PRIMARY KEY AUTO_INCREMENT,
    ORDER_ID INT NOT NULL,
    REPORT_URL VARCHAR(255),
    INTERPRETATION VARCHAR(255),
    REPORTING_PATHOLOGIST VARCHAR(255),
    FOREIGN KEY (ORDER_ID) REFERENCES Orders(ORDER_ID)
);
CREATE TABLE Billing (
    BILLING_ID INT PRIMARY KEY AUTO_INCREMENT,
    ORDER_ID INT NOT NULL,
    BILLED_AMOUNT DECIMAL(10,2) NOT NULL,
    PAYMENT_STATUS VARCHAR(255) NOT NULL,
    INSURANCE_CLAIM_STATUS VARCHAR(255),
    FOREIGN KEY (ORDER_ID) REFERENCES Orders(ORDER_ID)
);



