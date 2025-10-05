#!/usr/bin/env python3
"""
Quick test of improved table parser for Sec360
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.analysis.simple_parser import SimpleTableParser

def test_table_parser():
    """Test the table parser with real data"""
    
    # Real response from Ollama
    test_response = '''### Output Table

| Lines | Sensitive Fields | Sensitive Data | PII | HEPA | Medical | Compliance/API | Risk Score |
|-------|------------------|----------------|-----|------|---------|----------------|------------|
| 42    | 3                | 5              | 1   | 0    | 0       | 3              | 57         |'''
    
    parser = SimpleTableParser()
    
    print("Testing table parser with real Ollama response...")
    print("Input:", repr(test_response[:100]))
    
    result = parser.parse_analysis_table(test_response)
    print("Parsed data:", result)
    
    if result:
        formatted = parser.format_table(result)
        print("Formatted output:")
        print(formatted)
        
        # Check risk calculation
        from core.analysis.risk_calculator import RiskCalculator
        calculator = RiskCalculator()
        risk_result = calculator.calculate_risk_score(result)
        
        print("\nRisk Analysis:")
        print(f"  Score: {risk_result['risk_score']}/100")
        print(f"  Level: {risk_result['risk_level']}")
        print(f"  Confidence: {risk_result['confidence']:.2f}")
        
        print("\nFactors:")
        for factor in risk_result['contributing_factors']:
            print(f"  • {factor}")
        
    else:
        print("❌ No data parsed!")

if __name__ == "__main__":
    test_table_parser()
