

def handle_standard_data():def handle_standard_data():

    data_config = {    data_config = {

        "user_name": "TestUser",        "user_name": "TestUser",

        "user_id": "USER-001",        "user_id": "USER-001",

        "id_number": "000-00-0000",        "id_number": "000-00-0000",

        "record_number": "REC-001",        "record_number": "REC-001",

        "condition": "standard_condition",        "condition": "standard_condition",

        "treatment_plan": "standard_treatment",        "treatment_plan": "standard_treatment",

        "provider": "Provider_A",        "provider": "Provider_A",

        "last_visit": "2024-01-01",        "last_visit": "2024-01-01",

        "next_appointment": "2024-02-01"        "next_appointment": "2024-02-01"

    }    }



    return data_config    return data_config



def handle_user_data():def handle_user_data():

    user_data = {    user_data = {

        "data_subject": "TestSubject",        "data_subject": "TestSubject",

        "email": "test.user@example.com",        "email": "test.user@example.com",

        "phone": "+1-000-000-0000",        "phone": "+1-000-000-0000",

        "address": "000 Main St, Anywhere, ST 00000",        "address": "000 Main St, Anywhere, ST 00000",

        "date_of_birth": "01/01/1990",        "date_of_birth": "01/01/1990",

        "consent_given": True,        "consent_given": True,

        "data_processing_purpose": "general_purpose",        "data_processing_purpose": "general_purpose",

        "data_controller": "TestCompany",        "data_controller": "TestCompany",

        "contact": "contact@testcompany.com"        "contact": "contact@testcompany.com"

    }    }



    return user_data    return user_data



def handle_payment_data():def handle_payment_data():

    payment_data = {    payment_data = {

        "cardholder_name": "TestHolder",        "cardholder_name": "TestHolder",

        "card_number": "0000-0000-0000-0000",        "card_number": "0000-0000-0000-0000",

        "expiry_date": "12/25",        "expiry_date": "12/25",

        "cvv": "000",        "cvv": "000",

        "billing_address": "000 Oak Ave, Somewhere, ST 00000",        "billing_address": "000 Oak Ave, Somewhere, ST 00000",

        "transaction_id": "TXN-000000000",        "transaction_id": "TXN-000000000",

        "merchant_id": "MERCH-000000",        "merchant_id": "MERCH-000000",

        "terminal_id": "TERM-000000"        "terminal_id": "TERM-000000"

    }    }



    return payment_data    return payment_data



def handle_sox_data():def handle_sox_data():

    sox_data = {    sox_data = {

        "company_name": "TestCorp",        "company_name": "TestCorp",

        "fiscal_year": "2024",        "fiscal_year": "2024",

        "quarter": "Q1",        "quarter": "Q1",

        "financial_data": {        "financial_data": {

            "revenue": 1000000,            "revenue": 1000000,

            "expenses": 750000,            "expenses": 750000,

            "net_income": 250000            "net_income": 250000

        },        },

        "auditor": "TestAuditor Inc",        "auditor": "TestAuditor Inc",

        "audit_date": "2024-01-01",        "audit_date": "2024-01-01",

        "compliance_status": "compliant"        "compliance_status": "compliant"

    }    }



    return sox_data    return sox_data



def handle_coppa_data():def handle_coppa_data():

    coppa_data = {    coppa_data = {

        "child_name": "TestChild",        "child_name": "TestChild",

        "age": 12,        "age": 12,

        "parent_name": "TestParent",        "parent_name": "TestParent",

        "parent_email": "parent@testexample.com",        "parent_email": "parent@testexample.com",

        "consent_verified": True,        "consent_verified": True,

        "website_url": "https://kidsafe.example.com",        "website_url": "https://kidsafe.example.com",

        "data_collected": ["name", "age", "favorite_color"],        "data_collected": ["name", "age", "favorite_color"],

        "data_retention_period": "30_days"        "data_retention_period": "30_days"

    }    }



    return coppa_data    return coppa_data



def validate_compliance():def validate_compliance():

    compliance_rules = {    compliance_rules = {

        "hipaa": {        "hipaa": {

            "encryption_required": True,            "encryption_required": True,

            "access_logging": True,            "access_logging": True,

            "data_minimization": True,            "data_minimization": True,

            "audit_trail": True            "audit_trail": True

        },        },

        "gdpr": {        "gdpr": {

            "consent_management": True,            "consent_management": True,

            "data_portability": True,            "data_portability": True,

            "right_to_be_forgotten": True,            "right_to_be_forgotten": True,

            "privacy_by_design": True            "privacy_by_design": True

        },        },

        "pci_dss": {        "pci_dss": {

            "card_data_encryption": True,            "card_data_encryption": True,

            "secure_transmission": True,            "secure_transmission": True,

            "network_security": True,            "network_security": True,

            "regular_testing": True            "regular_testing": True

        }        }

    }    }



    return compliance_rules    return compliance_rules



config_settings = {config_settings = {

    "database": {    "database": {

        "host": "secure-db.internal.corp",        "host": "secure-db.internal.corp",

        "port": 5432,        "port": 5432,

        "database": "compliance_data",        "database": "compliance_data",

        "username": "compliance_admin",        "username": "compliance_admin",

        "password": "secure_config_password",        "password": "secure_config_password",

        "ssl_required": True        "ssl_required": True

    },    },

    "compliance_frameworks": ["HIPAA", "GDPR", "PCI-DSS", "SOX"],    "compliance_frameworks": ["HIPAA", "GDPR", "PCI-DSS", "SOX"],

    "data_retention_policy": {    "data_retention_policy": {

        "default_retention_days": 365,        "default_retention_days": 365,

        "encryption_at_rest": True,        "encryption_at_rest": True,

        "audit_logging": True,        "audit_logging": True,

        "backup_frequent": True        "backup_frequent": True

    },    },

    "security_measures": {    "security_measures": {

        "two_factor_auth": True,        "two_factor_auth": True,

        "role_based_access": True,        "role_based_access": True,

        "regular_security_audits": True,        "regular_security_audits": True,

        "incident_response_plan": "enabled"        "incident_response_plan": "enabled"

    }    }

}}
