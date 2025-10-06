# Sample Code File 3: Medical Records and Health Information
# This file contains medical data that should NOT be shared with AI tools

def process_medical_record():
    # Patient information
    patient_id = "PAT-123456"
    
    # Medical history
    medical_data = {
        "patient_id": "PAT-123456",
        "date_of_birth": "01/15/1985",
        "ssn": "123-45-6789",
        "diagnosis": "Type 2 Diabetes",
        "medications": ["Metformin", "Insulin"],
        "allergies": ["Penicillin", "Shellfish"],
        "blood_type": "O+",
        "medical_record_number": "MR-789012"
    }
    
    return medical_data

def handle_prescription():
    prescription_data = {
        "patient_id": "PAT-654321",
        "prescription_id": "RX-456789",
        "medication": "Lisinopril 10mg",
        "dosage": "Once daily",
        "prescribing_doctor": "Dr. Johnson",
        "pharmacy": "CVS Pharmacy",
        "insurance_id": "INS-123456789"
    }
    
    return prescription_data

def process_lab_results():
    lab_results = {
        "patient_id": "PAT-987654",
        "lab_order_id": "LAB-321654",
        "test_date": "2024-01-15",
        "results": {
            "glucose": "150 mg/dL",
            "cholesterol": "220 mg/dL",
            "blood_pressure": "140/90",
            "weight": "180 lbs",
            "height": "5'10\""
        },
        "physician": "Dr. Williams",
        "medical_record_number": "MR-456789"
    }
    
    return lab_results

def handle_insurance_claim():
    claim_data = {
        "patient_id": "PAT-147258",
        "claim_number": "CLM-963852",
        "insurance_provider": "Blue Cross Blue Shield",
        "policy_number": "BCBS-741852963",
        "group_number": "GRP-852741963",
        "diagnosis_code": "E11.9",
        "procedure_code": "99213",
        "billing_amount": 150.00,
        "patient_ssn": "987-65-4321"
    }
    
    return claim_data

def process_mental_health_record():
    mental_health_data = {
        "patient_id": "PAT-369258",
        "therapist": "Dr. Anderson",
        "session_date": "2024-01-20",
        "diagnosis": "Generalized Anxiety Disorder",
        "medications": ["Sertraline 50mg", "Lorazepam 0.5mg"],
        "therapy_notes": "Patient reports improved sleep patterns...",
        "next_appointment": "2024-01-27",
        "emergency_contact": "Mary Brown - (555) 123-4567"
    }
    
    return mental_health_data

# Medical database configuration
medical_db_config = {
    "database": {
        "host": "medical-db.internal.corp",
        "port": 5432,
        "database": "medical_records",
        "username": "med_admin",
        "password": "med_secret_123"
    },
    "compliance_enabled": True,
    "encryption_key": "hipaa_encryption_key_12345",
    "audit_logging": True
}

# Patient lookup function
def find_patient_by_ssn(ssn):
    # This function should not be shared as it contains SSN lookup logic
    patients = {
        "123-45-6789": "John Doe",
        "987-65-4321": "Jane Smith",
        "456-78-9012": "Robert Johnson"
    }
    return patients.get(ssn, "Patient not found")
