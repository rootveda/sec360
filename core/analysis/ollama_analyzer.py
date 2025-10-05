#!/usr/bin/env python3
"""
Sec360 Ollama Analyzer
Implements Ollama-based code analysis using system prompts
for structured security analysis and compliance detection.
"""

import os
import json
import time
from typing import Dict, List, Optional, Generator
import requests
from pathlib import Path

class OllamaAnalyzer:
    def __init__(self, ollama_client=None, base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama Analyzer
        
        Args:
            ollama_client: Existing Ollama client instance
            base_url: Ollama service URL
        """
        from core.llm.ollama_client import OllamaClient
        
        self.ollama_client = ollama_client or OllamaClient(base_url)
        self.system_prompt = self.load_system_prompt()
        self.results_cache = {}
        
    def load_system_prompt(self) -> str:
        """Load the system prompt for analysis"""
        prompt_file = Path(__file__).parent.parent.parent / "system_prompts" / "analysis_prompt.txt"
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to default prompt
            return self.get_default_system_prompt()
    
    def get_default_system_prompt(self) -> str:
        """Default system prompt if file not found"""
        return """You are an expert secure code reviewer specializing in **Sensitive Data & Compliance Detection**. 
You will be provided with a code snippet. 
Your task is to analyze it using the following rules:

1. Count the **total number of lines of code analysed** (ignoring empty lines and comments).
2. Identify and count **Sensitive Fields**:
   - Variables, function parameters, configuration keys, or field names that may hold sensitive data.
   - Examples: "jwt_token", "ssn", "patient_name", "credit_card_number", "api_key", "secret", "password".
3. Identify and count **Sensitive Data Instances**:
   - Explicit string values, assigned data, or embedded literals that are sensitive.
   - For example: `"eyJhb...jwt..."` → counts as one Sensitive Data instance.
4. Classify each Sensitive Data found into categories:
   - **PII (Personally Identifiable Information)** → SSN, address, email, phone number, username.
   - **Medical (HIPAA-related/health details)** → patient name, diagnoses, prescriptions, medical ID.
   - **HEPA / Healthcare Data** → insurance ID, hospital records, EMR fields.
   - **API / Secrets / Compliance (Security-related)** → jwt token, api keys, client secrets, passwords.
5. Count the number of items flagged under each classification.
6. Calculate a **Risk Score (0–100)** based on:
   - Number of lines analyzed (more lines lowers risk per line).
   - Higher Sensitive Fields Count increases score.
   - Higher Sensitive Data Count increases score.
   - Each compliance flag category raises the risk.
   - Use balanced logic (e.g., baseline score from fields + weighted on categories).

### Output Format
Produce a single markdown table with the following columns:

- Lines of Code Analysed  
- Sensitive Fields Count  
- Sensitive Data Count  
- PII Count  
- HEPA Count  
- Medical Count  
- Compliance/API Count  
- Risk Score (0–100)

### Important Notes:
- Analyze ONLY the actual code provided
- Do NOT use placeholder or example values
- Count only what is actually present in the code
- If no sensitive data is found, use 0 for counts
- Base risk score on actual findings, not examples

Be very strict in identifying sensitive variables, even when uncertain."""

    def analyze_code(self, code_snippet: str, model: str = "llama3.2:3b") -> Dict:
        """
        Analyze code snippet using Ollama model
        
        Args:
            code_snippet: Code to analyze
            model: Ollama model to use
            
        Returns:
            Dict containing analysis metadata and results
        """
        analysis_session_id = f"analysis_{int(time.time())}"
        
        try:
            # Ensure Ollama is running and model is available
            if not self.ollama_client.check_ollama_status():
                return {
                    "error": "Ollama service not available",
                    "session_id": analysis_session_id,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # Check if model is available
            available_models = self.ollama_client.get_available_models()
            if model not in available_models:
                return {
                    "error": f"Model {model} not available. Available models: {available_models}",
                    "session_id": analysis_session_id,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # Prepare the prompt
            full_prompt = f"{self.system_prompt}\n\nCode snippet to analyze:\n```\n{code_snippet}\n```"
            
            # Send to Ollama for analysis
            print(f"🔍 Analyzing code with model: {model}")
            
            # Set the model in Ollama client
            self.ollama_client.set_model(model)
            
            # Generate response
            response_data = self.ollama_client.generate_response(full_prompt, stream=False)
            
            if not response_data:
                return {
                    "error": "Failed to get response from Ollama",
                    "session_id": analysis_session_id,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # Extract response text from dictionary
            response_text = response_data.get('response', '')
            
            if not response_text:
                return {
                    "error": "Empty response from Ollama",
                    "session_id": analysis_session_id,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # Parse JSON response
            try:
                from core.analysis.json_parser import JsonParser
                parser = JsonParser()
                analysis_table = parser.parse_json_response(response_text)
                # Note: parse_json_response already calls validate_analysis_data internally
            except Exception as e:
                print(f"JSON parsing failed, falling back to table extraction: {e}")
                analysis_table = self.extract_analysis_table(response_text)
            
            result = {
                "session_id": analysis_session_id,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "model_used": model,
                "code_length": len(code_snippet.split('\n')),
                "raw_response": response_text,  # Keep text for compatibility
                "raw_response_data": response_data,  # Keep full data for token counting
                "analysis_table": analysis_table,
                "success": True
            }
            
            # Cache the result
            self.results_cache[analysis_session_id] = result
            
            return result
            
        except Exception as e:
            error_result = {
                "session_id": analysis_session_id,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "error": str(e),
                "success": False
            }
            return error_result
    
    def extract_analysis_table(self, response: str) -> Optional[Dict]:
        """
        Extract structured analysis table from Ollama response
        
        Args:
            response: Raw response from Ollama
            
        Returns:
            Dict with extracted analysis metrics or None if parsing fails
        """
        try:
            # Look for markdown table in response
            lines = response.split('\n')
            table_start = None
            table_end = None
            
            for i, line in enumerate(lines):
                if '|' in line and ('Lines' in line or 'Sensitive' in line):
                    if table_start is None:
                        table_start = i
                elif table_start is not None and '|' in line:
                    table_end = i
                elif table_start is not None and line.strip() == '':
                    if table_end is None:
                        table_end = i
            
            if table_start is None:
                return None
            
            # Extract table data
            table_lines = lines[table_start:table_end+1] if table_end else lines[table_start:]
            
            # Parse header and data rows
            if len(table_lines) < 2:
                return None
            
            header_line = table_lines[0]
            data_line = table_lines[2] if len(table_lines) > 2 else table_lines[1]
            
            # Clean up headers and data
            headers = [h.strip() for h in header_line.split('|')[1:-1]]
            data_values = [d.strip() for d in data_line.split('|')[1:-1]]
            
            if len(headers) != len(data_values):
                return None
            
            # Map to expected structure
            result = {}
            for header, value in zip(headers, data_values):
                clean_header = header.lower().replace(' ', '_').replace('/', '_')
                try:
                    # Try to convert to int for numeric values
                    result[clean_header] = int(value) if value.isdigit() else value
                except ValueError:
                    result[clean_header] = value
            
            return result
            
        except Exception as e:
            print(f"Error parsing analysis table: {e}")
            return None
    
    def get_analysis_history(self) -> List[Dict]:
        """Get analysis history"""
        return list(self.results_cache.values())
    
    def clear_cache(self):
        """Clear analysis cache"""
        self.results_cache.clear()
    
    def health_check(self) -> Dict:
        """Check analyzer health"""
        return {
            "ollama_status": self.ollama_client.check_ollama_status(),
            "available_models": self.ollama_client.get_available_models(),
            "system_prompt_loaded": bool(self.system_prompt),
            "cache_size": len(self.results_cache)
        }
