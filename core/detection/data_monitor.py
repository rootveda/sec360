#!/usr/bin/env python3
"""
Data Leak Monitor for LLM Safety Training
Monitors user input for potential data leaks without blocking the flow
"""

import re
import json
import logging
import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class FlagType(Enum):
    API_KEY = "API_KEY"
    TOKEN = "TOKEN"
    PASSWORD = "PASSWORD"
    SSN = "SSN"
    CREDIT_CARD = "CREDIT_CARD"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    MEDICAL = "MEDICAL"
    PII = "PII"
    GDPR = "GDPR"
    COMPLIANCE = "COMPLIANCE"
    HOSTNAME = "HOSTNAME"
    INTERNAL_IP = "INTERNAL_IP"
    SESSION_ID = "SESSION_ID"

@dataclass
class FlaggedContent:
    content: str
    flag_type: FlagType
    confidence: float
    position: Tuple[int, int]
    context: str
    timestamp: datetime.datetime

class DataLeakMonitor:
    def __init__(self, config_file: str = "core/monitor_config.json"):
        self.config = self._load_config(config_file)
        self.patterns = self._compile_patterns()
        self.session_logs = []
        
        # Cache to prevent re-processing the same input
        self.input_cache = {}
        self.cache_timeout = 30  # seconds
        
        self.setup_logging()
        
    def _load_config(self, config_file: str) -> Dict:
        """Load monitoring configuration"""
        default_config = {
            "api_key_patterns": [
                r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'(?i)(access[_-]?token|token)\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'(?i)(bearer[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?'
            ],
            "pii_patterns": [
                r'(?i)(ssn|social[_-]?security)\s*[:=]\s*["\']?(\d{3}-?\d{2}-?\d{4})["\']?',
                r'(?i)(credit[_-]?card|cc)\s*[:=]\s*["\']?(\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})["\']?',
                r'(?i)(email)\s*[:=]\s*["\']?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})["\']?',
                r'(?i)(phone|telephone)\s*[:=]\s*["\']?(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})["\']?'
            ],
            "medical_patterns": [
                r'(?i)(patient[_-]?name|patient_name)\s*[:=]\s*["\']?([a-zA-Z\s]+)["\']?',
                r'(?i)(medical[_-]?record|medical_record)\s*[:=]\s*["\']?([a-zA-Z0-9\s]+)["\']?',
                r'(?i)(diagnosis|illness|disease)\s*[:=]\s*["\']?([a-zA-Z\s]+)["\']?',
                r'(?i)(health[_-]?insurance|insurance[_-]?id)\s*[:=]\s*["\']?([a-zA-Z0-9]+)["\']?'
            ],
            "internal_patterns": [
                r'(?i)(hostname|host)\s*[:=]\s*["\']?([a-zA-Z0-9.-]+\.(internal|local|corp|company))["\']?',
                r'(?i)(internal[_-]?ip|private[_-]?ip)\s*[:=]\s*["\']?(192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[01])\.)["\']?',
                r'(?i)(session[_-]?id|sessionid)\s*[:=]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'(?i)(database[_-]?password|db[_-]?password)\s*[:=]\s*["\']?([a-zA-Z0-9!@#$%^&*()_+-=]+)["\']?'
            ],
            "compliance_keywords": [
                "hipaa", "gdpr", "sox", "pci", "ferpa", "ccpa", "compliance", "audit", "regulatory"
            ]
        }
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default_config
    
    def _compile_patterns(self) -> Dict[FlagType, List[re.Pattern]]:
        """Compile regex patterns for efficient matching"""
        patterns = {
            FlagType.API_KEY: [re.compile(p) for p in self.config["api_key_patterns"]],
            FlagType.PII: [re.compile(p) for p in self.config["pii_patterns"]],
            FlagType.MEDICAL: [re.compile(p) for p in self.config["medical_patterns"]],
            FlagType.HOSTNAME: [re.compile(p) for p in self.config["internal_patterns"]],
            FlagType.COMPLIANCE: [re.compile(p) for p in self.config.get("compliance_patterns", [])],
        }
        return patterns
    
    def setup_logging(self):
        """Setup logging for the monitor"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('core/logs/data_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def analyze_input(self, user_input: str, session_id: str) -> List[FlaggedContent]:
        """Analyze user input for potential data leaks using two-tier system:
        1. Potential flags: Count all sensitive fields regardless of value
        2. Detected flags: Count only fields with actual sensitive data"""
        import time
        
        # Check cache first
        input_hash = hash(user_input)
        current_time = time.time()
        
        if input_hash in self.input_cache:
            cached_time, cached_result = self.input_cache[input_hash]
            if current_time - cached_time < self.cache_timeout:
                # Return cached result without logging again
                self.logger.info(f"Using cached result for input (hash: {input_hash})")
                return cached_result
            else:
                # Remove expired cache entry
                del self.input_cache[input_hash]
        
        flagged_items = []
        seen_content = set()  # Global deduplication across all flag types
        
        # Only analyze if input looks like code or contains sensitive patterns
        if not self._is_code_like_input(user_input):
            return flagged_items
        
        # TIER 1: Count potential flags (all sensitive fields regardless of value)
        potential_flags = self._count_potential_flags(user_input)
        
        # TIER 2: Count detected flags (only fields with actual sensitive data)
        # Use a single method that determines flag type based on field name
        flagged_items.extend(self._check_all_patterns(user_input, seen_content))
        
        # Check for compliance keywords (use separate seen_content to avoid conflicts)
        compliance_seen = set()
        flagged_items.extend(self._check_compliance_keywords(user_input, compliance_seen))
        
        # VALIDATION: Ensure detected flags <= potential flags
        detected_count = len(flagged_items)
        if detected_count > potential_flags:
            self.logger.warning(f"VALIDATION ERROR: Detected flags ({detected_count}) > Potential flags ({potential_flags})")
            self.logger.warning("This violates the rule: detected_flags <= potential_flags")
            self.logger.warning("Applying deduplication to fix the issue...")
            
            # Apply additional deduplication by content similarity
            flagged_items = self._deduplicate_by_content_similarity(flagged_items)
            detected_count = len(flagged_items)
            
            if detected_count > potential_flags:
                self.logger.error(f"CRITICAL: After deduplication, detected flags ({detected_count}) still > potential flags ({potential_flags})")
                # Force limit to potential flags count
                flagged_items = flagged_items[:potential_flags]
                self.logger.warning(f"Forced limit: reduced detected flags to {potential_flags}")
        
        # Cache the result
        self.input_cache[input_hash] = (current_time, flagged_items)
        
        # Log flagged items with potential flag count
        for item in flagged_items:
            self._log_flagged_content(item, session_id, user_input, potential_flags)
        
        # Log session activity even if no flags (for tracking)
        if not flagged_items:
            self._log_session_activity(user_input, session_id, 0, potential_flags)
        
        return flagged_items
    
    def _analyze_without_logging(self, user_input: str) -> List[FlaggedContent]:
        """Analyze user input for potential data leaks without logging to files"""
        flagged_items = []
        seen_content = set()  # Global deduplication across all flag types
        
        # Only analyze if input looks like code or contains sensitive patterns
        if not self._is_code_like_input(user_input):
            return flagged_items
        
        # TIER 1: Count potential flags (all sensitive fields regardless of value)
        potential_flags = self._count_potential_flags(user_input)
        
        # TIER 2: Count detected flags (only fields with actual sensitive data)
        # Use a single method that determines flag type based on field name
        flagged_items.extend(self._check_all_patterns(user_input, seen_content))
        
        # Check for compliance keywords (use separate seen_content to avoid conflicts)
        compliance_seen = set()
        flagged_items.extend(self._check_compliance_keywords(user_input, compliance_seen))
        
        # VALIDATION: Ensure detected flags <= potential flags
        # Note: detected flags can exceed potential flags when there are multiple fields of the same type
        # (e.g., ssn_1, ssn_2 both count as detected flags but only 1 potential flag for 'ssn')
        detected_count = len(flagged_items)
        
        # Only apply deduplication if there are obvious duplicates
        # (same content from same field name)
        flagged_items = self._deduplicate_by_content_similarity(flagged_items)
        detected_count = len(flagged_items)
        
        # Return flagged items without logging to files
        return flagged_items
    
    def _deduplicate_by_content_similarity(self, flagged_items: List[FlaggedContent]) -> List[FlaggedContent]:
        """Remove duplicate detections based on content similarity"""
        if not flagged_items:
            return flagged_items
        
        # Track unique values to prevent over-counting
        unique_items = []
        seen_values = set()
        
        for item in flagged_items:
            # Normalize the content for comparison
            normalized_content = item.content.lower().strip()
            
            # Skip if we've already seen this exact value
            if normalized_content in seen_values:
                continue
            
            # Add to seen values
            seen_values.add(normalized_content)
            unique_items.append(item)
        
        return unique_items
    
    def _count_potential_flags(self, user_input: str) -> int:
        """Count all sensitive fields regardless of their values (field-based counting)"""
        potential_fields = set()  # Use set to avoid duplicates
        
        # Define field patterns for different data types (with numeric suffixes support)
        field_patterns = [
            # API Key fields
            r'(?i)(api[_-]?key|apikey|access[_-]?token|token|secret[_-]?key|secretkey|bearer[_-]?token|jwt[_-]?token|oauth[_-]?token|endpoint|google|stripe|aws|db[_-]?connection|connection|status)(?:_\d+)?\s*[:=]',
            # PII fields
            r'(?i)(ssn|social[_-]?security|credit[_-]?card|cc|email|phone|telephone|address|name|first[_-]?name|last[_-]?name|full[_-]?name|date[_-]?of[_-]?birth|dob|street|city|state|zip[_-]?code|number|expiry|cvv|account[_-]?number|routing[_-]?number|account[_-]?holder|tax[_-]?id|filing[_-]?status)(?:_\d+)?\s*[:=]',
            # Medical fields
            r'(?i)(patient[_-]?name|patient[_-]?id|medical[_-]?record|medical[_-]?history|diagnosis|illness|disease|prescription|medication|allergy|blood[_-]?type|health[_-]?insurance|insurance[_-]?id|prescription[_-]?id|dosage|prescribing[_-]?doctor|pharmacy|lab[_-]?order[_-]?id|test[_-]?date|glucose|cholesterol|blood[_-]?pressure|weight|height|physician|claim[_-]?number|insurance[_-]?provider|policy[_-]?number|group[_-]?number|diagnosis[_-]?code|procedure[_-]?code|patient[_-]?ssn|therapist|session[_-]?date|therapy[_-]?notes|next[_-]?appointment|emergency[_-]?contact|encryption[_-]?key|medical[_-]?record[_-]?number)(?:_\d+)?\s*[:=]',
            # Internal infrastructure fields
            r'(?i)(hostname|host|internal[_-]?ip|private[_-]?ip|session[_-]?id|sessionid|database[_-]?password|db[_-]?password|server[_-]?password|admin[_-]?password|password|username|database|user[_-]?service|payment[_-]?service|notification[_-]?service|admin[_-]?panel|server|protocol|ca[_-]?cert|client[_-]?cert|client[_-]?key|shared[_-]?secret|session[_-]?secret|redis[_-]?session[_-]?store|session[_-]?cookie[_-]?domain|admin[_-]?session[_-]?key|bind[_-]?password|gateway|api[_-]?server|namespace|service[_-]?account)(?:_\d+)?\s*[:=]',
            # Compliance fields
            r'(?i)(hipaa|gdpr|sox|pci|ferpa|ccpa|compliance|audit|regulatory|treatment[_-]?plan|last[_-]?visit|data[_-]?subject|data[_-]?processing[_-]?purpose|retention[_-]?period|data[_-]?controller|dpo[_-]?contact|cardholder[_-]?name|card[_-]?number|expiry[_-]?date|billing[_-]?address|transaction[_-]?id|merchant[_-]?id|terminal[_-]?id|company[_-]?name|fiscal[_-]?year|quarter|internal[_-]?controls|student[_-]?name|student[_-]?id|parent[_-]?guardian|math|science|english|history|attendance|disciplinary[_-]?records|consumer[_-]?name|ip[_-]?address|browser[_-]?fingerprint|audit[_-]?id|scope|remediation[_-]?due[_-]?date|regulation|requirement|implementation[_-]?date|compliance[_-]?deadline|penalties|data[_-]?protection[_-]?officer|privacy[_-]?policy[_-]?url|access[_-]?controls|data[_-]?retention[_-]?policy|penetration[_-]?testing|auditor|audit[_-]?date|compliance[_-]?status)(?:_\d+)?\s*[:=]'
        ]
        
        # Count all field occurrences regardless of their values
        for pattern in field_patterns:
            matches = re.findall(pattern, user_input)
            for match in matches:
                potential_fields.add(match.lower())  # Normalize to lowercase
        
        # Also check for JSON field names in quotes (with numeric suffixes support)
        json_field_patterns = [
            # API Key fields in JSON
            r'"(api[_-]?key|apikey|access[_-]?token|token|secret[_-]?key|secretkey|bearer[_-]?token|jwt[_-]?token|oauth[_-]?token|endpoint|google|stripe|aws|db[_-]?connection|connection|status)(?:_\d+)?"',
            # PII fields in JSON
            r'"(ssn|social[_-]?security|credit[_-]?card|cc|email|phone|telephone|address|name|first[_-]?name|last[_-]?name|full[_-]?name|date[_-]?of[_-]?birth|dob|street|city|state|zip[_-]?code|number|expiry|cvv|account[_-]?number|routing[_-]?number|account[_-]?holder|tax[_-]?id|filing[_-]?status)(?:_\d+)?"',
            # Medical fields in JSON
            r'"(patient[_-]?name|patient[_-]?id|medical[_-]?record|medical[_-]?history|diagnosis|illness|disease|prescription|medication|allergy|blood[_-]?type|health[_-]?insurance|insurance[_-]?id|prescription[_-]?id|dosage|prescribing[_-]?doctor|pharmacy|lab[_-]?order[_-]?id|test[_-]?date|glucose|cholesterol|blood[_-]?pressure|weight|height|physician|claim[_-]?number|insurance[_-]?provider|policy[_-]?number|group[_-]?number|diagnosis[_-]?code|procedure[_-]?code|patient[_-]?ssn|therapist|session[_-]?date|therapy[_-]?notes|next[_-]?appointment|emergency[_-]?contact|encryption[_-]?key|medical[_-]?record[_-]?number)(?:_\d+)?"',
            # Internal infrastructure fields in JSON
            r'"(hostname|host|internal[_-]?ip|private[_-]?ip|session[_-]?id|sessionid|database[_-]?password|db[_-]?password|server[_-]?password|admin[_-]?password|password|username|database|user[_-]?service|payment[_-]?service|notification[_-]?service|admin[_-]?panel|server|protocol|ca[_-]?cert|client[_-]?cert|client[_-]?key|shared[_-]?secret|session[_-]?secret|redis[_-]?session[_-]?store|session[_-]?cookie[_-]?domain|admin[_-]?session[_-]?key|bind[_-]?password|gateway|api[_-]?server|namespace|service[_-]?account)(?:_\d+)?"',
            # Compliance fields in JSON
            r'"(hipaa|gdpr|sox|pci|ferpa|ccpa|compliance|audit|regulatory|treatment[_-]?plan|last[_-]?visit|data[_-]?subject|data[_-]?processing[_-]?purpose|retention[_-]?period|data[_-]?controller|dpo[_-]?contact|cardholder[_-]?name|card[_-]?number|expiry[_-]?date|billing[_-]?address|transaction[_-]?id|merchant[_-]?id|terminal[_-]?id|company[_-]?name|fiscal[_-]?year|quarter|internal[_-]?controls|student[_-]?name|student[_-]?id|parent[_-]?guardian|math|science|english|history|attendance|disciplinary[_-]?records|consumer[_-]?name|ip[_-]?address|browser[_-]?fingerprint|audit[_-]?id|scope|remediation[_-]?due[_-]?date|regulation|requirement|implementation[_-]?date|compliance[_-]?deadline|penalties|data[_-]?protection[_-]?officer|privacy[_-]?policy[_-]?url|access[_-]?controls|data[_-]?retention[_-]?policy|penetration[_-]?testing|auditor|audit[_-]?date|compliance[_-]?status)(?:_\d+)?"'
        ]
        
        # Count JSON field occurrences
        for pattern in json_field_patterns:
            matches = re.findall(pattern, user_input)
            for match in matches:
                potential_fields.add(match.lower())  # Normalize to lowercase
        
        return len(potential_fields)
    
    def _get_potential_field_names(self, user_input: str) -> set:
        """Get all unique sensitive field names from the input"""
        potential_fields = set()
        
        # Define field patterns for different data types (with numeric suffixes support)
        field_patterns = [
            # API Key fields
            r'(?i)(api[_-]?key|apikey|access[_-]?token|token|secret[_-]?key|secretkey|bearer[_-]?token|jwt[_-]?token|oauth[_-]?token|endpoint|google|stripe|aws|db[_-]?connection|connection|status)(?:_\d+)?\s*[:=]',
            # PII fields
            r'(?i)(ssn|social[_-]?security|credit[_-]?card|cc|email|phone|telephone|address|name|first[_-]?name|last[_-]?name|full[_-]?name|date[_-]?of[_-]?birth|dob|street|city|state|zip[_-]?code|number|expiry|cvv|account[_-]?number|routing[_-]?number|account[_-]?holder|tax[_-]?id|filing[_-]?status)(?:_\d+)?\s*[:=]',
            # Medical fields
            r'(?i)(patient[_-]?name|patient[_-]?id|medical[_-]?record|medical[_-]?history|diagnosis|illness|disease|prescription|medication|allergy|blood[_-]?type|health[_-]?insurance|insurance[_-]?id|prescription[_-]?id|dosage|prescribing[_-]?doctor|pharmacy|lab[_-]?order[_-]?id|test[_-]?date|glucose|cholesterol|blood[_-]?pressure|weight|height|physician|claim[_-]?number|insurance[_-]?provider|policy[_-]?number|group[_-]?number|diagnosis[_-]?code|procedure[_-]?code|patient[_-]?ssn|therapist|session[_-]?date|therapy[_-]?notes|next[_-]?appointment|emergency[_-]?contact|encryption[_-]?key|medical[_-]?record[_-]?number)(?:_\d+)?\s*[:=]',
            # Internal infrastructure fields
            r'(?i)(hostname|host|internal[_-]?ip|private[_-]?ip|session[_-]?id|sessionid|database[_-]?password|db[_-]?password|server[_-]?password|admin[_-]?password|password|username|database|user[_-]?service|payment[_-]?service|notification[_-]?service|admin[_-]?panel|server|protocol|ca[_-]?cert|client[_-]?cert|client[_-]?key|shared[_-]?secret|session[_-]?secret|redis[_-]?session[_-]?store|session[_-]?cookie[_-]?domain|admin[_-]?session[_-]?key|bind[_-]?password|gateway|api[_-]?server|namespace|service[_-]?account)(?:_\d+)?\s*[:=]',
            # Compliance fields
            r'(?i)(hipaa|gdpr|sox|pci|ferpa|ccpa|compliance|audit|regulatory|treatment[_-]?plan|last[_-]?visit|data[_-]?subject|data[_-]?processing[_-]?purpose|retention[_-]?period|data[_-]?controller|dpo[_-]?contact|cardholder[_-]?name|card[_-]?number|expiry[_-]?date|billing[_-]?address|transaction[_-]?id|merchant[_-]?id|terminal[_-]?id|company[_-]?name|fiscal[_-]?year|quarter|internal[_-]?controls|student[_-]?name|student[_-]?id|parent[_-]?guardian|math|science|english|history|attendance|disciplinary[_-]?records|consumer[_-]?name|ip[_-]?address|browser[_-]?fingerprint|audit[_-]?id|scope|remediation[_-]?due[_-]?date|regulation|requirement|implementation[_-]?date|compliance[_-]?deadline|penalties|data[_-]?protection[_-]?officer|privacy[_-]?policy[_-]?url|access[_-]?controls|data[_-]?retention[_-]?policy|penetration[_-]?testing|auditor|audit[_-]?date|compliance[_-]?status)(?:_\d+)?\s*[:=]'
        ]
        
        # Extract field names from general patterns
        for pattern in field_patterns:
            matches = re.findall(pattern, user_input)
            for match in matches:
                potential_fields.add(match.lower())
        
        # Also check for JSON field names in quotes (with numeric suffixes support)
        json_field_patterns = [
            # API Key fields in JSON
            r'"(api[_-]?key|apikey|access[_-]?token|token|secret[_-]?key|secretkey|bearer[_-]?token|jwt[_-]?token|oauth[_-]?token|endpoint|google|stripe|aws|db[_-]?connection|connection|status)(?:_\d+)?"',
            # PII fields in JSON
            r'"(ssn|social[_-]?security|credit[_-]?card|cc|email|phone|telephone|address|name|first[_-]?name|last[_-]?name|full[_-]?name|date[_-]?of[_-]?birth|dob|street|city|state|zip[_-]?code|number|expiry|cvv|account[_-]?number|routing[_-]?number|account[_-]?holder|tax[_-]?id|filing[_-]?status)(?:_\d+)?"',
            # Medical fields in JSON
            r'"(patient[_-]?name|patient[_-]?id|medical[_-]?record|medical[_-]?history|diagnosis|illness|disease|prescription|medication|allergy|blood[_-]?type|health[_-]?insurance|insurance[_-]?id|prescription[_-]?id|dosage|prescribing[_-]?doctor|pharmacy|lab[_-]?order[_-]?id|test[_-]?date|glucose|cholesterol|blood[_-]?pressure|weight|height|physician|claim[_-]?number|insurance[_-]?provider|policy[_-]?number|group[_-]?number|diagnosis[_-]?code|procedure[_-]?code|patient[_-]?ssn|therapist|session[_-]?date|therapy[_-]?notes|next[_-]?appointment|emergency[_-]?contact|encryption[_-]?key|medical[_-]?record[_-]?number)(?:_\d+)?"',
            # Internal infrastructure fields in JSON
            r'"(hostname|host|internal[_-]?ip|private[_-]?ip|session[_-]?id|sessionid|database[_-]?password|db[_-]?password|server[_-]?password|admin[_-]?password|password|username|database|user[_-]?service|payment[_-]?service|notification[_-]?service|admin[_-]?panel|server|protocol|ca[_-]?cert|client[_-]?cert|client[_-]?key|shared[_-]?secret|session[_-]?secret|redis[_-]?session[_-]?store|session[_-]?cookie[_-]?domain|admin[_-]?session[_-]?key|bind[_-]?password|gateway|api[_-]?server|namespace|service[_-]?account)(?:_\d+)?"',
            # Compliance fields in JSON
            r'"(hipaa|gdpr|sox|pci|ferpa|ccpa|compliance|audit|regulatory|treatment[_-]?plan|last[_-]?visit|data[_-]?subject|data[_-]?processing[_-]?purpose|retention[_-]?period|data[_-]?controller|dpo[_-]?contact|cardholder[_-]?name|card[_-]?number|expiry[_-]?date|billing[_-]?address|transaction[_-]?id|merchant[_-]?id|terminal[_-]?id|company[_-]?name|fiscal[_-]?year|quarter|internal[_-]?controls|student[_-]?name|student[_-]?id|parent[_-]?guardian|math|science|english|history|attendance|disciplinary[_-]?records|consumer[_-]?name|ip[_-]?address|browser[_-]?fingerprint|audit[_-]?id|scope|remediation[_-]?due[_-]?date|regulation|requirement|implementation[_-]?date|compliance[_-]?deadline|penalties|data[_-]?protection[_-]?officer|privacy[_-]?policy[_-]?url|access[_-]?controls|data[_-]?retention[_-]?policy|penetration[_-]?testing|auditor|audit[_-]?date|compliance[_-]?status)(?:_\d+)?"'
        ]
        
        # Extract field names from JSON patterns
        for pattern in json_field_patterns:
            matches = re.findall(pattern, user_input)
            for match in matches:
                potential_fields.add(match.lower())
        
        return potential_fields
    
    def _check_patterns(self, text: str, flag_type: FlagType, seen_content: set) -> List[FlaggedContent]:
        """Check text against compiled patterns using field-based detection"""
        flagged_items = []
        
        # Get all potential field names from the text
        potential_fields = self._get_potential_field_names(text)
        
        # For each potential field, check if it has a non-empty value
        for field_name in potential_fields:
            # Find the actual field name in the text (with suffix if any)
            actual_field_name = self._find_actual_field_name(text, field_name)
            if not actual_field_name:
                continue
                
            # Check if this field has a non-empty value using field-specific patterns
            field_value = self._get_field_value(text, actual_field_name)
            
            if field_value:
                # Create a unique identifier for this field-value pair
                field_content_key = f"{field_name}:{field_value.lower().strip()}"
                
                # Skip if we've already seen this field-content combination
                if field_content_key in seen_content:
                    continue
                
                # Add to seen content to prevent duplicates
                seen_content.add(field_content_key)
                
                # Create a flagged item for this field-value pair
                flagged_item = FlaggedContent(
                    content=field_value,
                    flag_type=flag_type,
                    confidence=self._calculate_confidence(field_value, flag_type),
                    position=(0, len(field_value)),  # Position will be updated by caller if needed
                    context=f"{actual_field_name} = {field_value}",
                    timestamp=datetime.datetime.now()
                )
                flagged_items.append(flagged_item)
        
        return flagged_items
    
    def _find_actual_field_name(self, text: str, base_field_name: str) -> str:
        """Find the actual field name in the text (with suffix if any)"""
        # Look for field assignments with the base field name
        # Pattern: field_name = "value" or field_name_1 = "value", etc.
        pattern = rf'({re.escape(base_field_name)}(?:_\d+)?)\s*=\s*["\']?([^"\'\s,}}]+)["\']?'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        if matches:
            # Return the first match (actual field name)
            return matches[0][0]
        
        # Also check JSON format: "field_name": "value"
        json_pattern = rf'"({re.escape(base_field_name)}(?:_\d+)?)"\s*:\s*["\']?([^"\'\s,}}]+)["\']?'
        json_matches = re.findall(json_pattern, text, re.IGNORECASE)
        
        if json_matches:
            return json_matches[0][0]
        
        return None
    
    def _get_field_value(self, text: str, field_name: str) -> str:
        """Get the value for a specific field name from the text"""
        # Try exact field name first
        value = self._try_get_field_value(text, field_name)
        if value:
            return value
        
        # Try with numeric suffixes (e.g., ssn_1, ssn_2, etc.)
        if '_' in field_name and field_name.split('_')[-1].isdigit():
            base_field = '_'.join(field_name.split('_')[:-1])
            # Try all possible numeric suffixes
            for i in range(1, 10):  # Try _1 through _9
                suffixed_field = f"{base_field}_{i}"
                value = self._try_get_field_value(text, suffixed_field)
                if value:
                    return value
        
        return None
    
    def _try_get_field_value(self, text: str, field_name: str) -> str:
        """Try to get field value using exact field name"""
        # Pattern 1: field_name = "value" or field_name = value (handle multi-word values)
        pattern1 = rf'{re.escape(field_name)}\s*=\s*["\']([^"\']*)["\']'
        match1 = re.search(pattern1, text, re.IGNORECASE)
        if match1:
            value = match1.group(1).strip()
            if value and value not in ['""', "''", '']:
                return value
        
        # Pattern 2: "field_name": "value" (JSON) (handle multi-word values)
        pattern2 = rf'"{re.escape(field_name)}"\s*:\s*["\']([^"\']*)["\']'
        match2 = re.search(pattern2, text, re.IGNORECASE)
        if match2:
            value = match2.group(1).strip()
            if value and value not in ['""', "''", '']:
                return value
        
        # Pattern 3: field_name: "value" (YAML/other formats) (handle multi-word values)
        pattern3 = rf'{re.escape(field_name)}\s*:\s*["\']([^"\']*)["\']'
        match3 = re.search(pattern3, text, re.IGNORECASE)
        if match3:
            value = match3.group(1).strip()
            if value and value not in ['""', "''", '']:
                return value
        
        return None
    
    def _check_all_patterns(self, text: str, seen_content: set) -> List[FlaggedContent]:
        """Check all patterns and determine flag type based on field name"""
        flagged_items = []
        
        # Get all potential field names from the text
        potential_fields = self._get_potential_field_names(text)
        
        # Track which values we've already detected to prevent over-counting
        detected_values = set()
        
        # For each potential field, find all actual field names and process them
        for field_name in potential_fields:
            # Find all actual field names in the text (with suffix if any)
            actual_field_names = self._find_all_actual_field_names(text, field_name)
            
            # Process only the first occurrence of each field type to match potential count
            processed_field = False
            for actual_field_name in actual_field_names:
                if processed_field:
                    break
                    
                # Check if this field has a non-empty value
                field_value = self._get_field_value(text, actual_field_name)
                
                if field_value:
                    # Normalize the value for comparison
                    normalized_value = field_value.lower().strip()
                    
                    # Skip if we've already detected this exact value
                    if normalized_value in detected_values:
                        continue
                    
                    # Add to detected values to prevent duplicates
                    detected_values.add(normalized_value)
                    
                    # Create a unique identifier for this field-content pair
                    field_content_key = f"{actual_field_name}:{normalized_value}"
                    
                    # Skip if we've already seen this field-content combination
                    if field_content_key in seen_content:
                        continue
                    
                    # Add to seen content to prevent duplicates
                    seen_content.add(field_content_key)
                    
                    # Determine flag type based on field name
                    flag_type = self._determine_flag_type(field_name)
                    
                    # Create a flagged item for this field-value pair
                    flagged_item = FlaggedContent(
                        content=field_value,
                        flag_type=flag_type,
                        confidence=self._calculate_confidence(field_value, flag_type),
                        position=(0, len(field_value)),  # Position will be updated by caller if needed
                        context=f"{actual_field_name} = {field_value}",
                        timestamp=datetime.datetime.now()
                    )
                    flagged_items.append(flagged_item)
                    processed_field = True
        
        return flagged_items
    
    def _find_all_actual_field_names(self, text: str, base_field_name: str) -> List[str]:
        """Find all actual field names in the text (with suffix if any)"""
        actual_fields = []
        
        # Look for field assignments with the base field name
        # Pattern: field_name = "value" or field_name_1 = "value", etc.
        pattern = rf'({re.escape(base_field_name)}(?:_\d+)?)\s*=\s*["\']([^"\']*)["\']'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for match in matches:
            actual_field_name = match[0]
            if actual_field_name not in actual_fields:
                actual_fields.append(actual_field_name)
        
        # Also check JSON format: "field_name": "value"
        json_pattern = rf'"({re.escape(base_field_name)}(?:_\d+)?)"\s*:\s*["\']([^"\']*)["\']'
        json_matches = re.findall(json_pattern, text, re.IGNORECASE)
        
        for match in json_matches:
            actual_field_name = match[0]
            if actual_field_name not in actual_fields:
                actual_fields.append(actual_field_name)
        
        return actual_fields
    
    def _determine_flag_type(self, field_name: str) -> FlagType:
        """Determine flag type based on field name"""
        field_lower = field_name.lower()
        
        # Medical fields (check first to avoid conflicts with PII)
        if any(keyword in field_lower for keyword in ['patient', 'medical', 'record', 'history', 'diagnosis', 'illness', 'disease', 'prescription', 'medication', 'allergy', 'blood', 'type', 'health', 'insurance', 'dosage', 'prescribing', 'doctor', 'pharmacy', 'lab', 'order', 'test', 'date', 'glucose', 'cholesterol', 'pressure', 'weight', 'height', 'physician', 'claim', 'provider', 'policy', 'group', 'code', 'procedure', 'therapist', 'session', 'therapy', 'notes', 'appointment', 'emergency', 'contact', 'encryption']):
            return FlagType.MEDICAL
        
        # PII fields (check before API_KEY to avoid conflicts)
        elif any(keyword in field_lower for keyword in ['ssn', 'social', 'credit', 'card', 'cc', 'email', 'phone', 'telephone', 'address', 'name', 'first', 'last', 'full', 'date', 'birth', 'dob', 'street', 'city', 'state', 'zip', 'code', 'number', 'expiry', 'cvv', 'account', 'routing', 'holder', 'tax', 'id', 'filing', 'status']):
            return FlagType.PII
        
        # API Key fields
        elif any(keyword in field_lower for keyword in ['api', 'token', 'key', 'secret', 'bearer', 'jwt', 'oauth', 'endpoint', 'google', 'stripe', 'aws', 'connection']):
            return FlagType.API_KEY
        
        # Internal infrastructure fields
        elif any(keyword in field_lower for keyword in ['hostname', 'host', 'internal', 'ip', 'private', 'session', 'database', 'password', 'db', 'server', 'admin', 'root', 'username', 'user', 'service', 'payment', 'notification', 'panel', 'protocol', 'cert', 'client', 'shared', 'redis', 'cookie', 'domain', 'bind', 'gateway', 'namespace', 'account']):
            return FlagType.HOSTNAME
        
        # Compliance fields
        elif any(keyword in field_lower for keyword in ['hipaa', 'gdpr', 'sox', 'pci', 'ferpa', 'ccpa', 'compliance', 'audit', 'regulatory', 'treatment', 'plan', 'visit', 'data', 'subject', 'processing', 'purpose', 'retention', 'period', 'controller', 'dpo', 'contact', 'cardholder', 'billing', 'transaction', 'merchant', 'terminal', 'company', 'fiscal', 'year', 'quarter', 'controls', 'student', 'parent', 'guardian', 'math', 'science', 'english', 'history', 'attendance', 'disciplinary', 'records', 'consumer', 'browser', 'fingerprint', 'scope', 'remediation', 'due', 'regulation', 'requirement', 'implementation', 'deadline', 'penalties', 'protection', 'officer', 'privacy', 'policy', 'url', 'access', 'penetration', 'testing', 'auditor', 'compliance_status']):
            return FlagType.COMPLIANCE
        
        # Default to PII for unknown fields (most common case)
        else:
            return FlagType.PII
    
    def _extract_field_name_from_match(self, text: str, match, potential_fields: set) -> str:
        """Extract the field name associated with a pattern match"""
        match_start = match.start()
        match_end = match.end()
        
        # Look backwards from the match to find the field name
        # Check for patterns like: field_name = "value" or "field_name": "value"
        
        # Look for assignment pattern: field_name = "value"
        before_match = text[max(0, match_start-100):match_start]
        
        # Pattern 1: field_name = "value"
        assignment_pattern = r'(\w+)\s*=\s*["\']?[^"\']*["\']?\s*$'
        assignment_match = re.search(assignment_pattern, before_match)
        if assignment_match:
            field_name = assignment_match.group(1).lower()
            if field_name in potential_fields:
                return field_name
        
        # Pattern 2: "field_name": "value" (JSON)
        json_pattern = r'"(\w+)"\s*:\s*["\']?[^"\']*["\']?\s*$'
        json_match = re.search(json_pattern, before_match)
        if json_match:
            field_name = json_match.group(1).lower()
            if field_name in potential_fields:
                return field_name
        
        # Pattern 3: field_name: "value" (YAML/other formats)
        colon_pattern = r'(\w+)\s*:\s*["\']?[^"\']*["\']?\s*$'
        colon_match = re.search(colon_pattern, before_match)
        if colon_match:
            field_name = colon_match.group(1).lower()
            if field_name in potential_fields:
                return field_name
        
        # If no field name found, check if the content itself contains field indicators
        content = match.group(0).lower()
        for field in potential_fields:
            if field in content:
                return field
        
        return None
    
    def _check_compliance_keywords(self, text: str, seen_content: set) -> List[FlaggedContent]:
        """Check for compliance-related keywords, but ignore comments and function names"""
        flagged_items = []
        text_lower = text.lower()
        
        for keyword in self.config["compliance_keywords"]:
            if keyword in text_lower and keyword not in seen_content:
                # Find all occurrences of the keyword
                start = 0
                while True:
                    start_pos = text_lower.find(keyword, start)
                    if start_pos == -1:
                        break
                    
                    # Check if this occurrence is in a comment or function name
                    # Look at the context around the keyword
                    context_start = max(0, start_pos - 50)
                    context_end = min(len(text), start_pos + len(keyword) + 50)
                    context = text[context_start:context_end]
                    
                    # Skip if it's in a comment (starts with # or //)
                    if context.strip().startswith('#') or context.strip().startswith('//'):
                        start = start_pos + 1
                        continue
                    
                    # Skip if it's in a function name (preceded by def or function)
                    if 'def ' in context or 'function ' in context:
                        start = start_pos + 1
                        continue
                    
                    # Skip if it's in a string literal (surrounded by quotes)
                    if context.count('"') % 2 == 1 or context.count("'") % 2 == 1:
                        start = start_pos + 1
                        continue
                    
                    # Skip if it's in a multi-line comment or docstring
                    if '"""' in context or "'''" in context:
                        start = start_pos + 1
                        continue
                    
                    # Skip if it's in a variable assignment or function call
                    if '=' in context or '(' in context:
                        start = start_pos + 1
                        continue
                    
                    # This is a valid compliance keyword detection
                    flagged_item = FlaggedContent(
                        content=keyword,
                        flag_type=FlagType.COMPLIANCE,
                        confidence=0.8,
                        position=(start_pos, start_pos + len(keyword)),
                        context=text[max(0, start_pos-50):start_pos+len(keyword)+50],
                        timestamp=datetime.datetime.now()
                    )
                    flagged_items.append(flagged_item)
                    seen_content.add(keyword)
                    break  # Only flag the first valid occurrence
        
        return flagged_items
    
    def _calculate_confidence(self, content: str, flag_type: FlagType) -> float:
        """Calculate confidence score for flagged content"""
        base_confidence = {
            FlagType.API_KEY: 0.9,
            FlagType.PII: 0.85,
            FlagType.MEDICAL: 0.8,
            FlagType.HOSTNAME: 0.75,
            FlagType.COMPLIANCE: 0.7
        }
        
        return base_confidence.get(flag_type, 0.5)
    
    def _log_flagged_content(self, flagged_item: FlaggedContent, session_id: str, user_input: str = "", potential_flags: int = 0):
        """Log flagged content to file and session logs"""
        log_entry = {
            "session_id": session_id,
            "timestamp": flagged_item.timestamp.isoformat(),
            "flag_type": flagged_item.flag_type.value,
            "content": flagged_item.content,
            "confidence": flagged_item.confidence,
            "position": flagged_item.position,
            "context": flagged_item.context,
            "input_preview": user_input[:2000] + "..." if len(user_input) > 2000 else user_input,
            "potential_flags": potential_flags
        }
        
        self.session_logs.append(log_entry)
        
        # Log to file
        self.logger.warning(f"FLAGGED [{flagged_item.flag_type.value}] - {flagged_item.content}")
        
        # Write to JSON log file
        with open(f"core/logs/session_{session_id}.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def _log_session_activity(self, user_input: str, session_id: str, flag_count: int, potential_flags: int = 0):
        """Log session activity even when no flags are detected"""
        log_entry = {
            "session_id": session_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "flag_type": "NO_FLAGS",
            "content": user_input,  # Use the actual message instead of generic flag count
            "confidence": 1.0,
            "position": (0, len(user_input)),
            "context": f"Input length: {len(user_input)} characters",
            "input_preview": user_input[:2000] + "..." if len(user_input) > 2000 else user_input,
            "potential_flags": potential_flags
        }
        
        self.session_logs.append(log_entry)
        
        # Log to file
        self.logger.info(f"SESSION_ACTIVITY [{session_id}] - {flag_count} flags detected in user input")
        
        # Write to JSON log file
        with open(f"core/logs/session_{session_id}.json", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def _is_code_like_input(self, user_input: str) -> bool:
        """Check if input looks like code or contains sensitive patterns"""
        input_lower = user_input.lower().strip()
        
        # Skip very short inputs (likely just greetings)
        if len(input_lower) < 10:
            return False
        
        # Skip common greetings and conversational phrases
        greetings = [
            "hello", "hi", "hey", "how are you", "thanks", "thank you",
            "good morning", "good afternoon", "good evening", "bye", "goodbye",
            "what", "how", "why", "when", "where", "who", "can you", "could you",
            "please", "help", "assist", "explain", "tell me", "show me", "analyze"
        ]
        
        for greeting in greetings:
            if input_lower.startswith(greeting):
                return False
        
        # Check for JSON structure (more flexible than requiring 30 lines)
        if user_input.strip().startswith('{') and user_input.strip().endswith('}'):
            return True
        
        # Check for minimum line count (reduced from 30 to 5 for JSON structures)
        lines = user_input.split("\n")
        if len(lines) < 5:
            return False
        
        # Check for code-like patterns
        code_indicators = [
            "def ", "class ", "function", "import ", "from ", "return ",
            "if ", "for ", "while ", "try:", "except:", "with ",
            "api_key", "password", "secret", "token", "key",
            "database", "server", "host", "port", "url",
            "email", "phone", "address", "name", "ssn",
            "patient", "medical", "diagnosis", "prescription"
        ]
        
        for indicator in code_indicators:
            if indicator in input_lower:
                return True
        
        # Check for indentation (Python code)
        indented_lines = [line for line in lines if line.startswith("    ") or line.startswith("\t")]
        if len(indented_lines) > 2:  # Reduced from 5 to 2
            return True
        
        # Check for code structure (functions, classes, etc.)
        code_structure_count = 0
        for line in lines:
            line_stripped = line.strip()
            if (line_stripped.startswith("def ") or 
                line_stripped.startswith("class ") or 
                line_stripped.startswith("import ") or 
                line_stripped.startswith("from ") or
                line_stripped.startswith("if ") or
                line_stripped.startswith("for ") or
                line_stripped.startswith("while ") or
                line_stripped.startswith("try:") or
                line_stripped.startswith("except:") or
                line_stripped.startswith("with ")):
                code_structure_count += 1
        
        if code_structure_count >= 2:  # Reduced from 3 to 2
            return True
        
        return False
    
    def get_session_score(self, session_id: str) -> Dict:
        """Calculate session score based on flagged items"""
        session_flags = [log for log in self.session_logs if log["session_id"] == session_id]
        
        if not session_flags:
            return {"score": 100, "total_flags": 0, "breakdown": {}}
        
        # Calculate score based on flag types and confidence
        score = 100
        breakdown = {}
        
        for flag in session_flags:
            flag_type = flag["flag_type"]
            confidence = flag["confidence"]
            
            # Deduct points based on flag type and confidence
            deduction = {
                "API_KEY": 15,
                "PII": 12,
                "MEDICAL": 10,
                "HOSTNAME": 8,
                "COMPLIANCE": 5
            }.get(flag_type, 3)
            
            score -= deduction * confidence
            breakdown[flag_type] = breakdown.get(flag_type, 0) + 1
        
        return {
            "score": max(0, score),
            "total_flags": len(session_flags),
            "breakdown": breakdown,
            "session_id": session_id
        }
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all session data"""
        sessions = {}
        for log in self.session_logs:
            session_id = log["session_id"]
            if session_id not in sessions:
                sessions[session_id] = []
            sessions[session_id].append(log)
        
        return [{"session_id": sid, "logs": logs} for sid, logs in sessions.items()]

if __name__ == "__main__":
    # Test the monitor
    monitor = DataLeakMonitor()
    
    test_inputs = [
        "api_key: abcdef1234567890",
        "patient_name: John Doe",
        "ssn: 123-45-6789",
        "hostname: internal-server.corp",
        "This is normal code without any sensitive data"
    ]
    
    for i, test_input in enumerate(test_inputs):
        flagged = monitor.analyze_input(test_input, f"test_session_{i}")
        print(f"Input: {test_input}")
        print(f"Flagged: {len(flagged)} items")
        for flag in flagged:
            print(f"  - {flag.flag_type.value}: {flag.content}")
        print()
