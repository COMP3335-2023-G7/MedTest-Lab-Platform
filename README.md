# MedTest Lab Platform

## Tech Stacks (LAMP Stack)

- Container
  - Docker
  
- Frontend
  - HTML + CSS + JS

- Backend
  - Python 3

- Database
  - MySQL

## Code Usage

- To run the Docker file 

  ```bash
  docker-compose up -d --build
  ```

## Role Actions
- Lab Staff
  - Check & Add Test(s)
  - Check & Write Test Result(s)
- Patient
  - Check & Booking Appointment(s)
  - Check Test Result(s)
  - Pay Bill(s)
- Sectary
	- Manage Appointment(s)
	- Make order(s)
	- Confirm Payment

## Database Design

- Patients

  | PATIENT_ID | NAME | BIRTHDATE | CONTACT | INSURANCE_DETAILS | PASSWORD | SALT |
  | ---------- | ---- | --------- | ------- | ----------------- | -------- | ---- |
  |            |      |           |         |                   |          |      |

- Tests Catalog

  | TEST_CODE | NAME | DESCRIPTION | COST |
  | --------- | ---- | ----------- | ---- |
  |           |      |             |      |

- Orders

  | ORDER_ID | PATIENT_ID | TEST_CODE | ORDERING_PHYSICIAN | ORDER_DATE | STATUS |
  | -------- | ---------- | --------- | ------------------ | ---------- | ------ |
  |          |            |           |                    |            |        |

- Appointments

  | APPOINTMENT_ID | PATIENT_ID | DATETIME |
  | -------------- | ---------- | -------- |
  |                |            |          |

- Results

  | RESULT_ID | ORDER_ID | REPORT_URL | INTERPRETATION | REPORTING_PATHOLOGIST |
  | --------- | -------- | ---------- | -------------- | --------------------- |
  |           |          |            |                |                       |

- Billing

  | BILLING_ID | ORDER_ID | BILLED_AMOUNT | PAYMENT_STATUS | INSURANCE_CLAIM_STATUS |
  | ---------- | -------- | ------------- | -------------- | ---------------------- |
  |            |          |               |                |                        |

- Staff

  | STAFF_ID | NAME | ROLE | CONTACT | PASSWORD |
  | -------- | ---- | ---- | ------- | -------- |
  |          |      |      |         |          |
