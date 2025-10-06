# Sample Code File 2: Personal Identifiable Information (PII)
# This file contains PII data that should NOT be shared with AI tools

def process_user_data():
    # Social Security Numbers
    ssn_1 = "123-45-6789"
    ssn_2 = "987654321"
    
    # Credit Card Numbers
    credit_card_1 = "4532-1234-5678-9012"
    credit_card_2 = "5555555555554444"
    
    # Email addresses
    email_1 = "john.doe@example.com"
    email_2 = "jane.smith@company.com"
    
    # Phone numbers
    phone_1 = "+1-555-123-4567"
    phone_2 = "(555) 987-6543"
    
    # Addresses
    address_1 = "123 Main Street, Anytown, NY 12345"
    address_2 = "456 Oak Avenue, Somewhere, CA 90210"
    
    # Date of birth
    dob_1 = "01/15/1985"
    dob_2 = "12-25-1990"
    
    return {}

def create_user_profile():
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "address": {
            "street": "123 Main Street",
            "city": "Anytown",
            "state": "NY",
            "zip_code": "12345"
        },
        "credit_card": {
            "expiry": "12/25",
            "cvv": "123"
        }
    }
    
    return user_data

def process_financial_data():
    # Bank account information
    bank_account = {
        "account_number": "1234567890",
        "routing_number": "021000021"
    }
    
    # Tax information
    tax_info = {
        "tax_id": "12-3456789",
        "filing_status": "single",
        "annual_income": 75000
    }
    
    return {"bank": bank_account, "tax": tax_info}

# Configuration with PII
user_config = {
    "default_user": {
        "name": "John Doe",
        "ssn": "123-45-6789",
        "email": "john.doe@example.com",
        "phone": "+1-555-123-4567",
        "credit_card": "4532-1234-5678-9012",
        "address": "123 Main Street, Anytown, NY 12345"
    },
    "backup_user": {
        "name": "Jane Smith",
        "ssn": "987-65-4321", 
        "email": "jane.smith@company.com",
        "phone": "(555) 987-6543",
        "credit_card": "5555555555554444",
        "address": "456 Oak Avenue, Somewhere, CA 90210"
    },
    "admin_user": {
        "name": "Admin User",
        "ssn": "111-22-3333",
        "email": "admin@company.com",
        "phone": "+1-800-555-0199",
        "credit_card": "4111111111111111",
        "address": "789 Admin Lane, Corporate City, TX 75001"
    }
}

# Additional sensitive data arrays
customer_data = [
    {"name": "Alice Johnson", "ssn": "444-55-6666", "email": "alice@email.com"},
    {"name": "Bob Wilson", "ssn": "777-88-9999", "email": "bob@email.com"},
    {"name": "Carol Davis", "ssn": "000-11-2222", "email": "carol@email.com"}
]

# Financial records
financial_records = {
    "account_1": {"number": "1234567890", "balance": 50000, "ssn": "123-45-6789"},
    "account_2": {"number": "0987654321", "balance": 25000, "ssn": "987-65-4321"},
    "account_3": {"number": "1122334455", "balance": 75000, "ssn": "111-22-3333"}
}
