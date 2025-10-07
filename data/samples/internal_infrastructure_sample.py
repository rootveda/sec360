
def get_database_config():
    db_config = {
        "hostname": "db-prod-01.internal.corp",
        "internal_ip": "192.168.1.100",
        "port": 5432,
        "username": "db_admin",
        "password": "super_secret_db_password",
        "database": "production_db"
    }
    
    return db_config

def get_api_endpoints():
    endpoints = {
        "user_service": "https://user-api.internal.corp:8080",
        "payment_service": "https://payment-api.internal.corp:8081",
        "notification_service": "https://notify-api.internal.corp:8082",
        "admin_panel": "https://admin.internal.corp:8443"
    }
    
    return endpoints

def get_internal_services():
    services = {
        "redis": {
            "host": "redis-cluster.internal.corp",
            "port": 6379,
            "password": "redis_secret_123"
        },
        "elasticsearch": {
            "host": "es-master.internal.corp",
            "port": 9200,
            "username": "es_admin",
            "password": "elastic_secret_456"
        },
        "kafka": {
            "brokers": [
                "kafka-01.internal.corp:9092",
                "kafka-02.internal.corp:9092",
                "kafka-03.internal.corp:9092"
            ],
            "username": "kafka_user",
            "password": "kafka_secret_789"
        }
    }
    
    return services

def get_vpn_config():
    vpn_config = {
        "server": "vpn.internal.corp",
        "port": 1194,
        "protocol": "udp",
        "ca_cert": "/etc/vpn/ca.crt",
        "client_cert": "/etc/vpn/client.crt",
        "client_key": "/etc/vpn/client.key",
        "shared_secret": "vpn_shared_secret_abc123"
    }
    
    return vpn_config

def get_session_config():
    session_config = {
        "session_secret": "session_secret_key_xyz789",
        "session_timeout": 3600,
        "redis_session_store": "redis://redis-sessions.internal.corp:6379",
        "session_cookie_domain": ".internal.corp",
        "admin_session_key": "admin_session_secret_123"
    }
    
    return session_config

def get_monitoring_config():
    monitoring = {
        "prometheus": {
            "host": "prometheus.internal.corp",
            "port": 9090,
            "username": "prom_admin",
            "password": "prometheus_secret_456"
        },
        "grafana": {
            "host": "grafana.internal.corp",
            "port": 3000,
            "username": "grafana_admin",
            "password": "grafana_secret_789"
        },
        "jaeger": {
            "host": "jaeger.internal.corp",
            "port": 16686
        }
    }
    
    return monitoring

def get_ldap_config():
    ldap_config = {
        "server": "ldap.internal.corp",
        "port": 389,
        "base_dn": "dc=internal,dc=corp",
        "bind_dn": "cn=admin,dc=internal,dc=corp",
        "bind_password": "ldap_admin_password_123",
        "user_search_base": "ou=users,dc=internal,dc=corp"
    }
    
    return ldap_config

network_config = {
    "subnets": [
        "192.168.1.0/24",
        "192.168.2.0/24",
        "10.0.0.0/8"
    ],
    "dns_servers": [
        "192.168.1.10",
        "192.168.1.11"
    ],
    "gateway": "192.168.1.1",
    "internal_domains": [
        "internal.corp",
        "dev.internal.corp",
        "staging.internal.corp",
        "prod.internal.corp"
    ]
}

deployment_config = {
    "kubernetes": {
        "api_server": "https://k8s-api.internal.corp:6443",
        "namespace": "production",
        "service_account": "deploy-sa",
        "token": "k8s_service_account_token_abc123"
    },
    "docker_registry": {
        "host": "registry.internal.corp",
        "port": 5000,
        "username": "docker_admin",
        "password": "docker_registry_secret_456"
    }
}
