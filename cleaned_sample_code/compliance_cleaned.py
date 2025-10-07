
def handle_standard_data():
    data_config = {
        "user_name": "TestUser",
        "user_id": "USER-001",
        "id_number": "000-00-0000",
        "record_number": "REC-001",
        "condition": "standard_condition",
        "treatment_plan": "standard_treatment",
        "provider": "Provider_A",
        "last_visit": "2024-01-01",
        "next_appointment": "2024-02-01"
    }

    return data_config

def handle_user_data():
    user_data = {
        "data_subject": "TestSubject",
        "email": "test.user@example.com",
        "phone": "+1-000-000-0000",
        "address": "000 Main St, Anywhere, ST 00000",
        "date_of_birth": "01/01/1990",
        "consent_given": True,
        "data_processing_purpose": "general_purpose",
        "data_controller": "TestCompany",
        "contact": "contact@testcompany.com"
    }

    return user_data

def handle_payment_data():
    payment_data = {
        "cardholder_name": "TestHolder",
        "card_number": "0000-0000-0000-0000",
        "expiry_date": "12/25",
        "cvv": "000",
        "billing_address": "000 Oak Ave, Somewhere, ST 00000",
        "transaction_id": "TXN-000000000",
        "merchant_id": "MERCH-000000",
        "terminal_id": "TERM-000000"
    }

    return payment_data

def handle_sox_data():
    sox_data = {
        "company_name": "TestCorp",
        "fiscal_year": "2024",
        "quarter": "Q1",
        "financial_data": {
            "revenue": 1000000,
            "expenses": 750000,
            "net_income": 250000
        },
        "auditor": "TestAuditor Inc",
        "audit_date": "2024-01-01",
        "compliance_status": "compliant"
    }

    return sox_data

def handle_coppa_data():
    coppa_data = {
        "child_name": "TestChild",
        "age": 12,
        "parent_name": "TestParent",
        "parent_email": "parent@testexample.com",
        "consent_verified": True,
        "website_url": "https://kidsafe.example.com",
        "data_collected": ["name", "age", "favorite_color"],
        "data_retention_period": "30_days"
    }

    return coppa_data

def validate_compliance():
    compliance_rules = {
        "hipaa": {
            "encryption_required": True,
            "access_logging": True,
            "data_minimization": True,
            "audit_trail": True
        },
        "gdpr": {
            "consent_management": True,
            "data_portability": True,
            "right_to_be_forgotten": True,
            "privacy_by_design": True
        },
        "pci_dss": {
            "card_data_encryption": True,
            "secure_transmission": True,
            "network_security": True,
            "regular_testing": True
        }
    }

    return compliance_rules

config_settings = {
    "database": {
        "host": "secure-db.internal.corp",
        "port": 5432,
        "database": "compliance_data",
        "username": "compliance_admin",
        "password": "secure_config_password",
        "ssl_required": True
    },
    "compliance_frameworks": ["HIPAA", "GDPR", "PCI-DSS", "SOX"],
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
        "incident_response_plan": "enabled"
    }
}
