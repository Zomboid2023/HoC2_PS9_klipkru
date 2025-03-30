import json
import subprocess
from datetime import datetime

def log(message):
    """Helper function for logging with timestamps."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [LOG]: {message}")

def get_patient_records_for_doctor(doctor_name):
    """Fetches medical records assigned to a specific doctor from the blockchain."""
    loag(f"Fetching records for doctor: {doctor_name}")

    command = ["multichain-cli", "healthcarechain", "liststreamitems", "medical_records_stream"]
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        log(f"Error fetching records: {result.stderr}")
        return []

    try:
        records = json.loads(result.stdout)
        return [item["data"]["json"] for item in records if item["data"]["json"].get("doctor_name") == doctor_name]
    except json.JSONDecodeError:
        log("Error decoding blockchain response")
        return []

def upload_prescription_for_patient(doctor_name, patient_name, prescription_text):
    """Uploads a prescription to the blockchain for a specific patient."""
    try:
        log(f"Uploading prescription for patient: {patient_name} by doctor: {doctor_name}")

        record_entry = {
            "json": {
                "doctor_name": doctor_name,
                "patient_name": patient_name,
                "prescription": prescription_text,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        command = ["multichain-cli", "healthcarechain", "publish", "medical_records_stream", f"record_{patient_name}", json.dumps(record_entry)]
        result = subprocess.run(command, capture_output=True, text=True)

        return {"message": "Prescription uploaded"} if result.returncode == 0 else {"error": "Failed to store prescription"}
    except Exception as e:
        log(f"Exception Occurred: {e}")
        return {"error": "Exception occurred while storing prescription"}
