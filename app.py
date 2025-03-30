from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
from blockchain import register_user, get_user, hash_password
from patient_dashboard import get_patient_records, upload_prescription
from doctor_dashboard import get_patient_records_for_doctor, upload_prescription_for_patient

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

def log(message):
    """Helper function for logging with timestamps."""
    timestamp = dateatime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [LOG]: {message}")

@app.route('/')
def home():
    log("Serving register.html")
    return render_template('register.html')

@app.route('/doctor_dashboard/<doctor_name>', methods=['GET'])
def doctor_dashboard(doctor_name):
    try:
        log(f"Fetching records for doctor: {doctor_name}")
        records = get_patient_records_for_doctor(doctor_name)
        return jsonify({"records": records})
    except Exception as e:
        log(f"Error fetching doctor records: {str(e)}")
        return jsonify({"error": "Failed to fetch records"}), 500



@app.route('/upload_prescription_doctor', methods=['POST'])
def upload_prescription_doctor():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        doctor_name = request.form.get("doctor_name")
        patient_name = request.form.get("patient_name")

        if not all([doctor_name, patient_name]):
            return jsonify({"error": "Missing doctor or patient name"}), 400

        prescription_text = "Prescription File Uploaded"  # Here you can integrate OCR if needed
        response = upload_prescription_for_patient(doctor_name, patient_name, prescription_text)
        
        return jsonify(response)
    except Exception as e:
        log(f"Error in prescription upload: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500




@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        log(f"Received Registration Request: {data}")

        user_data = {
            "name": data.get("name"),
            "age": data.get("age"),
            "role": data.get("role"),
            "password": data.get("password")
        }
        log(f"Parsed User Data: {user_data}")

        tx_id = register_user(user_data)
        if tx_id:
            log(f"User Registered Successfully with Transaction ID: {tx_id}")
            return jsonify({"message": "User registered successfully!", "tx_id": tx_id}), 201

        log("Registration Failed (User may already exist)")
        return jsonify({"error": "Registration failed. User may already exist."}), 400
    except Exception as e:
        log(f"Exception in Registration: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        log(f"Received Login Request: {data}")

        name = data.get("name")
        role = data.get("role")
        password = data.get("password")

        user_data = get_user(name, role)
        if user_data:
            hashed_input_password = hash_password(password)
            if user_data["password"] == hashed_input_password:
                log(f"User Found & Password Matched: {user_data}")
                return jsonify({"message": "Login successful!", "user_data": user_data}), 200
            else:
                log("Password Incorrect")
                return jsonify({"error": "Invalid password"}), 401

        log("User Not Found")
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        log(f"Exception in Login: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/patient_dashboard/<name>', methods=['GET'])
def patient_dashboard(name):
    try:
        log(f"Fetching records for patient: {name}")
        records = get_patient_records(name)
        return jsonify({"records": records})
    except Exception as e:
        log(f"Error fetching patient records: {str(e)}")
        return jsonify({"error": "Failed to fetch records"}), 500

@app.route('/upload_prescription', methods=['POST'])
def upload_prescription_endpoint():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        patient_name = request.form.get("name")

        if not patient_name:
            return jsonify({"error": "Patient name required"}), 400

        response = upload_prescription(patient_name, file)
        return jsonify(response)
    except Exception as e:
        log(f"Error in prescription upload: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    log("Starting Flask server...")
    app.run(debug=True)
