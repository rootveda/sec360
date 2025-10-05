#!/usr/bin/env python3
"""
Sec360 JSON Parser
Handles JSON parsing and validation for analysis results.
"""

import json
import re
from typing import Dict, List, Any, Optional

class JsonParser:
    """Parse and validate JSON analysis results"""
    
    def __init__(self):
        # Expected JSON structure
        self.expected_fields = {
            'lines_of_code': int,
            'sensitive_fields': int,
            'sensitive_data': int,
            'pii_count': int,
            'hepa_count': int,
            'medical_count': int,
            'compliance_api_count': int,
            'risk_score': int,
            'analysis_details': dict
        }
        
        # Field mapping from JSON to internal format
        self.field_mapping = {
            'lines_of_code': 'lines',
            'sensitive_fields': 'sensitive_fields',
            'sensitive_data': 'sensitive_data',
            'pii_count': 'pii',
            'hepa_count': 'hepa',
            'medical_count': 'medical',
            'compliance_api_count': 'compliance_api',
            'risk_score': 'risk_score'
        }
    
    def parse_json_response(self, text: str) -> Dict:
        """
        Parse JSON response from text
        
        Args:
            text: Raw text response from LLM
            
        Returns:
            Parsed JSON data
        """
        try:
            # Extract JSON from text
            json_text = self._extract_json_from_text(text)
            
            # Parse JSON
            data = json.loads(json_text)
            
            # Validate structure
            return self.validate_analysis_data(data)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            # Try fallback parsing
            return self._fallback_parse(text)
        except Exception as e:
            print(f"JSON parsing failed: {e}")
            return self._fallback_parse(text)
    
    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON content from text that might contain markdown"""
        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find JSON object boundaries
        start = text.find('{')
        end = text.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        
        return text.strip()
    
    def _fallback_parse(self, text: str) -> Dict:
        """Fallback parsing for malformed JSON responses"""
        data = {}
        
        # Extract key-value pairs using regex
        patterns = {
            'lines_of_code': r'"lines_of_code":\s*(\d+)',
            'sensitive_fields': r'"sensitive_fields":\s*(\d+)',
            'sensitive_data': r'"sensitive_data":\s*(\d+)',
            'pii_count': r'"pii_count":\s*(\d+)',
            'hepa_count': r'"hepa_count":\s*(\d+)',
            'medical_count': r'"medical_count":\s*(\d+)',
            'compliance_api_count': r'"compliance_api_count":\s*(\d+)',
            'risk_score': r'"risk_score":\s*(\d+)'
        }
        
        for field, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                try:
                    data[field] = int(match.group(1))
                except ValueError:
                    data[field] = 0
        
        # Add default values for missing fields
        for field in self.expected_fields:
            if field not in data:
                data[field] = 0 if field != 'analysis_details' else {}
        
        return self.validate_analysis_data(data)
    
    def validate_analysis_data(self, json_data: Dict) -> Dict:
        """
        Validate and normalize analysis data
        
        Args:
            json_data: Raw JSON data
            
        Returns:
            Validated and normalized data
        """
        validated_data = {}
        
        # Map JSON fields to internal format
        for json_field, internal_field in self.field_mapping.items():
            value = json_data.get(json_field, 0)
            
            # Ensure numeric values are integers
            if isinstance(value, (int, float)):
                validated_data[internal_field] = max(0, int(value))
            else:
                validated_data[internal_field] = 0
        
        # Handle analysis_details
        analysis_details = json_data.get('analysis_details', {})
        if isinstance(analysis_details, dict):
            validated_data['analysis_details'] = analysis_details
        else:
            validated_data['analysis_details'] = {}
        
        # Ensure risk_score is within bounds
        validated_data['risk_score'] = max(0, min(100, validated_data['risk_score']))
        
        return validated_data
    
    def extract_summary(self, data: Dict) -> List[str]:
        """
        Extract key summary points from analysis data
        
        Args:
            data: Validated analysis data
            
        Returns:
            List of summary points
        """
        summary = []
        
        # Risk level indicators based on LLM's risk score
        risk_score = data.get('risk_score', 0)
        if risk_score >= 95:
            summary.append("🚨 CRITICAL RISK: Immediate action required")
        elif risk_score >= 80:
            summary.append("🚨 HIGH RISK: Significant security risks detected")
        elif risk_score >= 60:
            summary.append("⚠️ MEDIUM RISK: Some security concerns identified")
        elif risk_score >= 30:
            summary.append("🟢 LOW RISK: Minor security improvements needed")
        else:
            summary.append("✅ MINIMAL RISK: Good security practices observed")
        
        # Flagged content summary
        total_flags = (data.get('pii', 0) + data.get('hepa', 0) + 
                      data.get('medical', 0) + data.get('compliance_api', 0))
        
        if total_flags > 0:
            summary.append(f"🚩 {total_flags} sensitive data instances flagged")
        
        # Specific categories
        if data.get('pii', 0) > 0:
            summary.append(f"👤 {data['pii']} PII instances detected")
        
        if data.get('medical', 0) > 0:
            summary.append(f"🏥 {data['medical']} medical data instances detected")
        
        if data.get('compliance_api', 0) > 0:
            summary.append(f"🔐 {data['compliance_api']} API/security instances detected")
        
        # Code metrics
        lines = data.get('lines', 0)
        if lines > 0:
            summary.append(f"📊 Analyzed {lines} lines of code")
        
        # Add recommendations if available
        if 'analysis_details' in data and 'recommendations' in data['analysis_details']:
            recommendations = data['analysis_details']['recommendations']
            if recommendations:
                summary.append(f"💡 {len(recommendations)} recommendations provided")
        
        return summary
    
    def format_analysis_data(self, data: Dict) -> str:
        """
        Format analysis data for display
        
        Args:
            data: Analysis data dictionary
            
        Returns:
            Formatted string representation
        """
        lines = []
        
        # Header
        lines.append("ANALYSIS METRICS:")
        lines.append("-" * 20)
        
        # Metrics
        lines.append(f"Lines of Code: {data.get('lines', 0)}")
        lines.append(f"Sensitive Fields: {data.get('sensitive_fields', 0)}")
        lines.append(f"Sensitive Data: {data.get('sensitive_data', 0)}")
        lines.append(f"PII Count: {data.get('pii', 0)}")
        lines.append(f"HEPA Count: {data.get('hepa', 0)}")
        lines.append(f"Medical Count: {data.get('medical', 0)}")
        lines.append(f"Compliance/API Count: {data.get('compliance_api', 0)}")
        lines.append(f"Risk Score: {data.get('risk_score', 0)}/100")
        
        # Risk level
        risk_score = data.get('risk_score', 0)
        if risk_score >= 95:
            risk_level = "CRITICAL"
        elif risk_score >= 80:
            risk_level = "HIGH"
        elif risk_score >= 60:
            risk_level = "MEDIUM"
        elif risk_score >= 30:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        lines.append(f"Risk Level: {risk_level}")
        
        return "\n".join(lines)
    
    def format_json_for_display(self, raw_response: str) -> str:
        """
        Format JSON response for display
        
        Args:
            raw_response: Raw JSON response string
            
        Returns:
            Formatted JSON string
        """
        try:
            # Parse and reformat JSON
            data = json.loads(raw_response)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except:
            # If JSON parsing fails, return the raw response
            return raw_response
    
    def get_risk_level(self, risk_score: int) -> str:
        """Get human-readable risk level"""
        if risk_score >= 95:
            return "CRITICAL"
        elif risk_score >= 80:
            return "HIGH"
        elif risk_score >= 60:
            return "MEDIUM"
        elif risk_score >= 30:
            return "LOW"
        else:
            return "MINIMAL"
