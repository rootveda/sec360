# Sample Code File 4: Internal Infrastructure and Hostnames (Cleaned)
# This file contains sanitized infrastructure configuration for secure testing

def get_database_config():
    # Database configuration
    db_config = {
        "hostname": "database.example.com",
        "internal_ip": "192.168.1.100",
        "port": 5432,
        "username": "db_user",
        "password": "config_password",
        "database": "general_db"
    }
    
    return db_config

def get_api_endpoints():
    # API endpoints configuration
    endpoints = {
        "service_a": "https://api-a.example.com:8080",
        "service_b": "https://api-b.example.com:8081",
        "service_c": "https://api-c.example.com:8082",
        "management_panel": "https://management.example.com:8443"
    }
    
    return endpoints

def get_internal_services():
    # Service configuration
    services = {
        "cache_service": {
            "host": "cache-cluster.example.com",
            "port": 6379,
            "password": "cache_config"
        },
        "search_service": {
            "host": "search-master.example.com",
            "port": 9200,
            "username": "search_user",
            "password": "search_config"
        },
        "messaging": {
            "brokers": [
                "msg-01.example.com:9092",
                "msg-02.example.com:9092",
                "msg-03.example.com:9092"
            ],
            "username": "msg_user",
            "password": "msg_config"
        }
    }
    
    return services

def get_env_configuration():
    # Quality environment configuration
    quality_env = {
        "environment": "quality",
        "database_url": "postgresql://qfuser:qfpassword@qfdb.example.com:5432/qfdatabase",
        "redis_url": "redis://qfredis.example.com:6379/0",
        "elasticsearch_url": "https://qfes.example.com:9200",
        "kafka_bootstrap_servers": "qfkafka-01.example.com:9092,qfkafka-02.example.com:9092",
        "s3_bucket": "qf-bucket-data",
        "logs_path": "/var/log/quality/"
    }
    
    return quality_env

def initialize_application():
    # Application initialization configuration
    app_config = {
        "name": "sample_application",
        "version": "1.0.0",
        "environment": "quality",
        "debug_mode": False,
        "features": {
            "analytics": True,
            "monitoring": True,
            "backup": True,
            "security": True
        },
        "dependencies": ["service_a", "service_b", "service_c"],
        "health_check_port": 8080
    }
    
    return app_config

def setup_monitoring():
    # Monitoring configuration
    monitoring_config = {
        "prometheus": {
            "host": "prometheus.example.com",
            "port": 9090,
            "scrape_interval": "15s"
        },
        "grafana": {
            "host": "grafana.example.com",
            "port": 3000,
            "admin_user": "gadmin",
            "admin_password": "grafana_config"
        },
        "alertmanager": {
            "host": "alertmanager.example.com",
            "port": 9093,
            "slack_webhook": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXX"
        }
    }
    
    return monitoring_config

def deploy_application():
    # Deployment configuration
    deployment_config = {
        "kubernetes": {
            "namespace": "sample-app",
            "replicas": 3,
            "memory_limit": "512Mi",
            "cpu_limit": "500m"
        },
        "docker": {
            "registry": "registry.containerlab.cloud",
            "image_tag": "sample-app:latest",
            "build_args": ["ENV=quality"]
        },
        "environments": {
            "host_env": "host-001.example.com",
            "host_env_path": "/opt/sample-app",
            "host_config_path": "/etc/sample-app",
            "log_path": "/var/log/sample-app"
        }
    }
    
    return deployment_config

# Global configuration
global_config = {
    "application_settings": {
        "name": "sample_application",
        "version": "1.0.0",
        "environment": "quality"
    },
    "security_settings": {
        "enable_ssl": True,
        "require_authentication": True,
        "session_timeout": 3600,
        "max_login_attempts": 5
    },
    "logging_config": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_path": "/var/log/sample-app.log",
        "max_file_size": "10MB",
        "backup_count": 5
    }
}
