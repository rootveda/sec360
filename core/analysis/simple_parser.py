#!/usr/bin/env python3
"""
Simple working table parser for Sec360 analysis
"""

import re
from typing import Dict, List

class SimpleTableParser:
    """Simple markdown table parser that works reliably"""
    
    def parse_analysis_table(self, response_text: str) -> Dict:
        """Parse analysis data from Ollama response"""
        
        # Initialize default values
        result = {
            'lines_of_code': 0,
            'sensitive_fields': 0,
            'sensitive_data': 0,
            'pii_count': 0,
            'hepa_count': 0,
            'medical_count': 0,
            'compliance_api_count': 0,
            'risk_score': 0
        }
        
        lines = response_text.split('\n')
        
        # First try to find a markdown table
        table_start = None
        for i, line in enumerate(lines):
            if '| Lines ' in line and '|' in line:
                table_start = i
                break
        
        if table_start is not None:
            # Parse table format
            table_lines = []
            for i in range(table_start, min(table_start + 5, len(lines))):
                line = lines[i].strip()
                if '|' in line and line.startswith('|'):
                    table_lines.append(line)
                elif len(table_lines) > 2:
                    break
            
            if len(table_lines) >= 3:
                # Parse headers
                header_line = table_lines[0]
                headers = [h.strip() for h in header_line.split('|')[1:-1]]
                
                # Parse data line (skip separator)
                data_line = table_lines[2] if len(table_lines) > 2 else table_lines[1]
                data_values = [d.strip() for d in data_line.split('|')[1:-1]]
                
                if len(headers) == len(data_values):
                    # Map to standard structure
                    for header, value in zip(headers, data_values):
                        clean_header = header.lower().replace(' ', '_').replace('/', '_')
                        try:
                            result[clean_header] = int(value) if value.isdigit() else value
                        except ValueError:
                            result[clean_header] = value
                    return result
        
        # If no table found, parse structured text format
        for line in lines:
            line = line.strip()
            
            # Look for "Total Lines of Code Analyzed"
            if 'Total Lines of Code Analyzed' in line or 'Lines of Code' in line:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    result['lines_of_code'] = int(numbers[0])
            
            # Look for sensitive fields count
            elif 'Sensitive Fields:' in line:
                # Count the fields listed after this line
                field_count = 0
                current_index = lines.index(line)
                for next_line in lines[current_index:current_index+10]:
                    if next_line.strip().startswith('- ') and ':' in next_line:
                        field_count += 1
                    elif next_line.strip() == '' and field_count > 0:
                        break
                result['sensitive_fields'] = field_count
            
            # Look for sensitive data instances
            elif 'Sensitive Data Instances:' in line:
                # Count the instances listed after this line
                data_count = 0
                current_index = lines.index(line)
                for next_line in lines[current_index:current_index+20]:
                    if next_line.strip().startswith('`') and '=' in next_line:
                        data_count += 1
                    elif next_line.strip() == '' and data_count > 0:
                        break
                result['sensitive_data'] = data_count
            
            # Look for category counts
            elif 'PII' in line and ':' in line:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    result['pii_count'] = int(numbers[0])
            elif 'HEPA' in line and ':' in line:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    result['hepa_count'] = int(numbers[0])
            elif 'Medical' in line and ':' in line:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    result['medical_count'] = int(numbers[0])
            elif 'API' in line and ':' in line:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    result['compliance_api_count'] = int(numbers[0])
            
            # Look for risk score
            elif 'Risk Score' in line:
                numbers = re.findall(r'\d+', line)
                if numbers:
                    result['risk_score'] = int(numbers[0])
        
        # If no structured data found, estimate from content
        if result['lines_of_code'] == 0:
            # Count non-empty, non-comment lines
            code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            result['lines_of_code'] = len(code_lines)
        
        # Estimate counts based on content if not explicitly found
        if result['sensitive_fields'] == 0:
            # Count lines with common sensitive field patterns
            sensitive_patterns = ['api_key', 'password', 'secret', 'token', 'key', 'credential']
            for line in lines:
                if any(pattern in line.lower() for pattern in sensitive_patterns):
                    result['sensitive_fields'] += 1
        
        if result['sensitive_data'] == 0:
            # Count lines with quoted strings that look like sensitive data
            for line in lines:
                if '"' in line and len(line.split('"')[1]) > 10:  # Long quoted strings
                    result['sensitive_data'] += 1
        
        # Calculate risk score if not provided
        if result['risk_score'] == 0:
            base_score = min(result['sensitive_fields'] * 10, 50)
            data_penalty = min(result['sensitive_data'] * 8, 25)
            category_penalty = (result['pii_count'] + result['hepa_count'] + 
                              result['medical_count'] + result['compliance_api_count']) * 5
            result['risk_score'] = min(base_score + data_penalty + category_penalty, 100)
        
        # Ensure risk score is within bounds
        result['risk_score'] = max(0, min(result['risk_score'], 100))
        
        return result
    
    def format_table(self, data: Dict) -> str:
        """Format data as markdown table"""
        headers = [
            "Lines of Code", "Sensitive Fields", "Sensitive Data", 
            "PII", "HEPA", "Medical", "Compliance/API", "Risk Score"
        ]
        
        keys = ['lines_of_code', 'sensitive_fields', 'sensitive_data', 'pii_count', 
                'hepa_count', 'medical_count', 'compliance_api_count', 'risk_score']
        
        # Build header row
        header_row = "| " + " | ".join(headers) + " |"
        
        # Build separator row
        separator_row = "|" + "|".join(["-------" for _ in headers]) + "|"
        
        # Build data row
        values = [str(data.get(key, 0)) for key in keys]
        data_row = "| " + " | ".join(values) + " |"
        
        return f"{header_row}\n{separator_row}\n{data_row}"
