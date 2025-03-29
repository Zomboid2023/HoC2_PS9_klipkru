import json
import subprocess
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS  # Enables cross-origin requests
from ocr import extract_text_from_image

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

def log(message):
    """Helper function for logging with timestamps."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [LOG]: {message}")

def get_patient_records(name):
    """Fetches medical records from the blockchain for a given patient name."""
    log(f"Fetching records for patient: {name}")

    command = [
        "multichain-cli", "healthcarechain", "liststreamkeyitems", "medical_records_stream", f"record_{name}"
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        log(f"Error fetching records: {result.stderr}")
        return []

    try:
        records = json.loads(result.stdout)
        log(f"Fetched Records: {records}")
        return [item["data"]["json"] for item in records]
    except json.JSONDecodeError:
        log("Error decoding blockchain response")
        return []

@app.route("/upload_prescription", methods=["POST"])
def upload_prescription(patient_name, file):
    """Process prescription image, extract text, and store in blockchain."""
    try:
        log(f"Processing prescription for {patient_name}")

        # Ensure 'uploads' directory exists
        if not os.path.exists("uploads"):
            os.makedirs("uploads")

        filename = f"prescription_{patient_name}.png"
        file_path = os.path.join("uploads", filename)
        file.save(file_path)

        extracted_text = extract_text_from_image(file_path)
        log(f"Extracted Text: {extracted_text}")

        if not extracted_text:
            return {"error": "Could not extract text from image"}

        record_key = f"record_{patient_name}"
        record_entry = {
            "json": {
                "patient_name": patient_name,
                "prescription": extracted_text,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        data_json = json.dumps(record_entry)

        command = [
            "multichain-cli", "healthcarechain", "publish", "medical_records_stream",
            record_key, data_json
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            log(f"Prescription uploaded successfully for {record_key}!")
            return {"message": "Prescription uploaded and stored on blockchain", "extracted_text": extracted_text}
        else:
            log(f"Command Error: {result.stderr.strip()}")
            return {"error": "Failed to store prescription"}

    except Exception as e:
        log(f"Exception Occurred: {e}")
        return {"error": "Exception occurred while storing prescription"}

    except Exception as e:
        log(f"Exception Occurred: {e}")
        return jsonify({"error": "Exception occurred while storing prescription"}), 500

@app.route('/patient_dashboard/<name>', methods=['GET'])
def patient_dashboard(name):
    """Fetch medical records for a patient."""
    try:
        log(f"Fetching records for patient: {name}")
        records = get_patient_records(name)  # Ensure this function works
        return jsonify({"records": records})
    except Exception as e:
        log(f"Error fetching patient records: {str(e)}")
        return jsonify({"error": "Failed to fetch records"}), 500

def get_patient_records_for_doctor(doctor_name):
    """Fetches medical records assigned to a specific doctor from the blockchain."""
    log(f"Fetching records for doctor: {doctor_name}")

    command = [
        "multichain-cli", "healthcarechain", "liststreamitems", "medical_records_stream"
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        log(f"Error fetching records: {result.stderr}")
        return []

    try:
        records = json.loads(result.stdout)
        # Filter records where the doctor matches
        doctor_records = [
            item["data"]["json"]
            for item in records if "doctor_name" in item["data"]["json"] and item["data"]["json"]["doctor_name"] == doctor_name
        ]
        
        log(f"Fetched Records for Doctor {doctor_name}: {doctor_records}")
        return doctor_records
    except json.JSONDecodeError:
        log("Error decoding blockchain response")
        return []


if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")  # Ensure uploads folder exists
    app.run(debug=True)
