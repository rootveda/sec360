# Sample Code File 2: Personal Identifiable Information (Cleaned)
# This file contains sanitized user data for secure testing

def process_user_data():
    # User identification
    user_id = "default_value"
    id_number = "000-00-0000"
    
    # Payment data
    card_number = "0000-0000-0000-0000"
    payment_data = "0000000000000000"
    
    # Contact information
    email_address = "test@example.com"
    user_email = ""
    
    # Phone numbers
    phone_number = "+1-000-000-0000"
    contact_phone = "(000) 000-0000"
    
    # Address data
    user_address = "000 Main Street, TestCity, ST 00000"
    billing_address = ""
    
    # Birth information
    birth_date = "01/01/1990"
    date_info = "12-31-1990"
    
    return {}

def create_user_profile():
    profile_data = {
        "first_name": "TestUser",
        "last_name": "TestSubject",
        "address": {
            "street": "000 Main Street",
            "city": "TestCity",
            "state": "TS",
            "zip_code": "00000"
        },
        "payment_card": {
            "expiry": "12/25",
            "cvv": "000"
        }
    }
    
    return profile_data

def process_financial_data():
    # Account data
    account_data = {
        "account_number": "0000000000",
        "routing_number": "000000000"
    }
    
    # Tax data
    tax_data = {
        "tax_id": "00-0000000",
        "filing_status": "single",
        "annual_income": 50000
    }
    
    return {"account": account_data, "tax": tax_data}

# User configuration
config_data = {
    "default_user": {
        "name": "default_value"
    },
    "backup_user": {
        "name": ""
    }
}
