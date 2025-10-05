# Sample Code File 1: API Keys and Tokens
# This file contains various API keys and tokens that should NOT be shared with AI tools

def authenticate_user():
    # API Key for external service
    api_key = "sk-1234567890abcdef1234567890abcdef"
    
    
    # Secret key for encryption
    secret_key = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
    
    # Bearer token
    bearer_token = "Bearer abcdef1234567890abcdef1234567890"
    
    # Database connection string with password
    db_connection = "postgresql://user:password123@db:5432/mydb"
    
    return {"status": "authenticated"}

def make_api_call():
    # OAuth token
    oauth_token = "ya29.a0AfH6SMC..."
    
    # JWT token
    jwt_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
    
    # API endpoint with embedded credentials
    endpoint = "https://api.example.com/v1/data?key=sk-9876543210fedcba9876543210fedcba"
    
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "X-API-Key": api_key
    }
    
    return headers

# Configuration with embedded secrets
config = {
    "api_keys": {
        "stripe": "sk_test_FAKE_STRIPE_KEY_FOR_DEMO_PURPOSES_ONLY",
        "aws": "AKIAIOSFODNN7EXAMPLE",
        "google": "AIzaSyBOti4mM-6x9WDnZIjIey21x6Q6x9WDnZI",
        "github": "ghp_FAKE_GITHUB_TOKEN_FOR_DEMO_PURPOSES_ONLY",
        "slack": "xoxb-FAKE-SLACK-TOKEN-FOR-DEMO-PURPOSES-ONLY",
        "discord": "FAKE-DISCORD-TOKEN-FOR-DEMO-PURPOSES-ONLY"
    },
    "database": {
        "password": "SuperSecretPassword123!",
        "connection_string": "mongodb://admin:password456@cluster0.mongodb.net:27017/mydb",
        "redis_auth": "redis://:auth_token_789@redis.example.com:6379"
    },
    "encryption": {
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...",
        "secret_salt": "mySecretSalt123456789",
        "jwt_secret": "jwt_secret_key_abcdef123456789"
    }
}
