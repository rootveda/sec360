# Sample Code File 5: Data Protection (Optimized)
# This file contains sanitized data protection configuration for secure testing

def handle_standard_data():
    data_config = {
        "user_name": "default_value",
        "user_id": "",
        "id_number": "000-00-0000",
        "record_number": "",
        "condition": "default_value",
        "treatment_plan": "default_value",
        "provider": "default_value",
        "last_visit": "2024-01-01",
        "next_appointment": "2024-02-01"
    }
    
    return data_config

def handle_user_data():
    user_data = {
        "data_subject": "default_value",
        "email": "test@example.com",
        "phone": "+1-000-000-0000",
        "address": "default_value",
        "date_of_birth": "01/01/1990",
        "consent_given": True,
        "data_processing_purpose": "default_value",
        "data_controller": "default_value",
        "contact": "default_value"
    }
    
    return user_data

def handle_payment_data():
    payment_data = {
        "cardholder_name": "default_value",
        "card_number": "0000-0000-0000-0000",
        "expiry_date": "12/25",
        "cvv": "000",
        "billing_address": "default_value",
        "transaction_id": "",
        "merchant_id": "",
        "terminal_id": ""
    }
    
    return payment_data

def validate_compliance():
    compliance_rules = {
        "framework_a": {
            "feature_1": True,
            "feature_2": True,
            "feature_3": True,
            "feature_4": True
        },
        "framework_b": {
            "feature_1": True,
            "feature_2": True,
            "feature_3": True,
            "feature_4": True
        }
    }
    
    return compliance_rules

# Configuration settings
app_config = {
    "database": {
        "host": "example.com",
        "port": 5432,
        "database": "default_value",
        "username": "default_value",
        "password": "default_value",
        "ssl_required": True
    },
    "compliance_frameworks": ["Framework_A", "Framework_B"],
    "data_retention_policy": {
        "default_retention_days": 365,
        "encryption_at_rest": True,
        "audit_logging": True,
        "backup_frequent": True
    },
    "security_measures": {
        "two_factor_auth": True,
        "role_based_access": True,
        "regular_security_audits": True,
        "incident_response_plan": "default_value"
    }
}
