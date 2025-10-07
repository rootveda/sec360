#test
def handle_hipaa_data():
    phi_data = {
        "patient_name": "John Doe",
        "patient_id": "PAT-123456",
        "ssn": "123-45-6789",
        "medical_record_number": "MR-789012",
        "diagnosis": "Hypertension",
        "treatment_plan": "Medication and lifestyle changes",
        "physician": "Dr. Smith",
        "last_visit": "2024-01-15",
        "next_appointment": "2024-02-15"
    }
    
    return phi_data

def handle_gdpr_data():
    gdpr_data = {
        "data_subject": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "+1-555-123-4567",
        "address": "123 Main St, Anytown, NY 12345",
        "date_of_birth": "01/15/1985",
        "consent_given": True,
        "data_processing_purpose": "Marketing",
        "data_controller": "Company ABC",
        "dpo_contact": "dpo@company.com"
    }
    
    return gdpr_data

def handle_pci_data():
    pci_data = {
        "cardholder_name": "Robert Johnson",
        "card_number": "4532-1234-5678-9012",
        "expiry_date": "12/25",
        "cvv": "123",
        "billing_address": "456 Oak Ave, Somewhere, CA 90210",
        "transaction_id": "TXN-789012345",
        "merchant_id": "MERCH-123456",
        "terminal_id": "TERM-789012"
    }
    
    return pci_data

def handle_sox_data():
    sox_data = {
        "company_name": "Public Company Inc",
        "fiscal_year": "2024",
        "quarter": "Q1",
        "revenue": 1000000,
        "expenses": 750000,
        "net_income": 250000,
        "reviewer": "Big Four Accounting",
        "review_date": "2024-01-31",
        "compliance_status": "Compliant",
        "internal_controls": "Effective"
    }
    
    return sox_data

def handle_ferpa_data():
    ferpa_data = {
        "student_name": "Sarah Wilson",
        "student_id": "STU-147258",
        "ssn": "987-65-4321",
        "date_of_birth": "03/20/2000",
        "parent_guardian": "Mary Wilson",
        "emergency_contact": "(555) 987-6543",
        "grades": {
            "math": "A",
            "science": "B+",
            "english": "A-",
            "history": "B"
        },
        "attendance": "95%",
        "disciplinary_records": "None"
    }
    
    return ferpa_data

def handle_ccpa_data():
    ccpa_data = {
        "consumer_name": "Michael Brown",
        "email": "michael.brown@example.com",
        "phone": "+1-555-456-7890",
        "address": "789 Pine St, Anytown, CA 90210",
        "ip_address": "192.168.1.100",
        "browser_fingerprint": "abc123def456",
        "purchase_history": ["Product A", "Product B"],
        "data_categories": ["Personal", "Commercial", "Biometric"],
        "third_party_sharing": True,
        "opt_out_status": False
    }
    
    return ccpa_data

def handle_review_data():
    review_data = {
        "review_id": "REV-2024-001",
        "reviewer": "Internal Review Team",
        "review_date": "2024-01-15",
        "scope": "IT Security Controls",
        "findings": [
            "Weak password policy",
            "Missing encryption on sensitive data",
            "Inadequate access controls"
        ],
        "recommendations": [
            "Implement strong password policy",
            "Encrypt all sensitive data",
            "Review and update access controls"
        ],
        "review_status": "Needs Improvement",
        "remediation_due_date": "2024-03-15"
    }
    
    return review_data

def handle_regulatory_data():
    regulatory_data = {
        "regulation": "GDPR Article 32",
        "requirement": "Security of processing",
        "implementation_date": "2018-05-25",
        "penalties": "Up to 4% of annual turnover",
        "privacy_policy_url": "https://company.com/privacy",
        "data_subject_rights": [
            "Right to access",
            "Right to rectification",
            "Right to erasure",
            "Right to portability"
        ]
    }
    
    return regulatory_data

compliance_config = {
    "pci_dss": {
        "enabled": True,
        "card_data_encryption": True,
        "network_segmentation": True,
        "vulnerability_scanning": True,
        "penetration_testing": "Annual"
    }
}
