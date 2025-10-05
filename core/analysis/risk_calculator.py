#!/usr/bin/env python3
"""
Sec360 Risk Calculator
Calculates risk scores based on analysis data.
"""

from typing import Dict, List, Tuple
import math

class RiskCalculator:
    """Calculate risk scores based on analysis metrics"""
    
    def __init__(self):
        # Risk scoring weights
        self.weights = {
            'lines_weight': 0.1,          # More lines = lower risk per line
            'fields_weight': 0.3,         # Sensitive fields impact
            'data_weight': 0.4,           # Actual sensitive data impact
            'category_weight': 0.2        # Different category risks
        }
        
        # Category-specific risk multipliers
        self.category_risks = {
            'pii': 1.0,           # High priority - personal data
            'medical': 1.2,       # Highest priority - HIPAA regulated
            'hepa': 1.1,         # Healthcare data - significant risk
            'compliance_api': 0.9  # Security data - important but expected
        }
        
        # Risk thresholds
        self.thresholds = {
            'low': 30,
            'medium': 60,
            'high': 80,
            'critical': 95
        }
    
    def calculate_risk_score(self, analysis_data: Dict) -> Dict:
        """
        Calculate comprehensive risk score
        
        Args:
            analysis_data: Analysis metrics dictionary
            
        Returns:
            Dictionary with risk score and details
        """
        # Use LLM's risk score if available, otherwise calculate our own
        llm_risk_score = analysis_data.get('risk_score', 0)
        
        if llm_risk_score > 0:
            # Use LLM's risk score
            risk_score = llm_risk_score
            risk_level = self._determine_risk_level(risk_score)
            confidence = 0.95  # High confidence in LLM analysis
        else:
            # Fallback to our calculation
            lines = analysis_data.get('lines', 0)
            sensitive_fields = analysis_data.get('sensitive_fields', 0)
            sensitive_data = analysis_data.get('sensitive_data', 0)
            
            category_counts = {
                'pii': analysis_data.get('pii', 0),
                'medical': analysis_data.get('medical', 0),
                'hepa': analysis_data.get('hepa', 0),
                'compliance_api': analysis_data.get('compliance_api', 0)
            }
            
            # Base calculations
            base_score = self._calculate_base_score(lines, sensitive_fields, sensitive_data)
            category_score = self._calculate_category_score(category_counts)
            
            # Combine scores
            risk_score = min(100, int(base_score + category_score))
            risk_level = self._determine_risk_level(risk_score)
            confidence = self._calculate_confidence(analysis_data)
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'confidence': confidence,
            'contributing_factors': self._analyze_factors(analysis_data),
            'recommendations': self._generate_recommendations(analysis_data, risk_level)
        }
    
    def _calculate_base_score(self, lines: int, fields: int, data: int) -> float:
        """Calculate base risk score from fundamental metrics"""
        if lines == 0:
            return 0
        
        # Normalize by lines of code (more lines = lower risk per line)
        field_risk = min(50, (fields * 0.1) * self.weights['fields_weight'])
        data_risk = min(40, (data * 8) * self.weights['data_weight'])  # Restored to 8x multiplier
        
        # Line normalization (inverse relationship)
        line_factor = max(0.1, min(1.0, self.weights['lines_weight'] / max(1, lines)))
        
        return (field_risk + data_risk) * line_factor
    
    def _calculate_category_score(self, category_counts: Dict[str, int]) -> float:
        """Calculate category-specific risk score"""
        category_score = 0
        
        for category, count in category_counts.items():
            if count > 0:
                multiplier = self.category_risks.get(category, 1.0)
                category_score += (count * multiplier) * self.weights['category_weight']
        
        return min(25, category_score)  # Cap category contribution
    
    def _determine_risk_level(self, risk_score: int) -> str:
        """Determine risk level based on score"""
        if risk_score >= self.thresholds['critical']:
            return 'critical'
        elif risk_score >= self.thresholds['high']:
            return 'high'
        elif risk_score >= self.thresholds['medium']:
            return 'medium'
        elif risk_score >= self.thresholds['low']:
            return 'low'
        else:
            return 'minimal'
    
    def _calculate_confidence(self, analysis_data: Dict) -> float:
        """Calculate confidence in risk assessment"""
        lines = analysis_data.get('lines', 0)
        total_fields = analysis_data.get('sensitive_fields', 0)
        total_data = analysis_data.get('sensitive_data', 0)
        
        if lines == 0:
            return 0.0
        
        # More lines analyzed and more detailed analysis = higher confidence
        line_factor = min(1.0, lines / 20)  # Confidence increases with more lines
        detail_factor = min(1.0, (total_fields + total_data) / 10)  # More findings = higher confidence
        
        base_confidence = 0.5  # Start with moderate confidence
        confidence = base_confidence + (line_factor * 0.3) + (detail_factor * 0.2)
        
        return min(1.0, confidence)
    
    def _analyze_factors(self, analysis_data: Dict) -> List[str]:
        """Analyze contributing factors to risk score"""
        factors = []
        
        lines = analysis_data.get('lines', 0)
        fields = analysis_data.get('sensitive_fields', 0)
        data = analysis_data.get('sensitive_data', 0)
        
        # Line count factors
        if lines > 100:
            factors.append("Large codebase increases complexity")
        elif lines < 10:
            factors.append("Small code snippet limits analysis depth")
        
        # Sensitive field factors
        if fields > 5:
            factors.append(f"Many sensitive fields ({fields}) indicate high-risk practices")
        elif fields > 0:
            factors.append(f"Sensitive fields present ({fields})")
        
        # Data instance factors
        if data > 5:
            factors.append(f"Multiple sensitive data instances ({data}) detected")
        elif data > 0:
            factors.append(f"Sensitive data instances present ({data})")
        
        # Category-specific factors
        categories = {
            'PII': analysis_data.get('pii', 0),
            'Medical': analysis_data.get('medical', 0),
            'HEPA': analysis_data.get('hepa', 0),
            'API/Security': analysis_data.get('compliance_api', 0)
        }
        
        for category, count in categories.items():
            if count > 0:
                if count > 3:
                    factors.append(f"High {category} exposure rate ({count} instances)")
                else:
                    factors.append(f"{category} data detected ({count} instances)")
        
        return factors if factors else ["No significant risk factors identified"]
    
    def _generate_recommendations(self, analysis_data: Dict, risk_level: str) -> List[str]:
        """Generate recommendations based on risk analysis"""
        recommendations = []
        
        if risk_level == 'critical':
            recommendations.extend([
                "🚨 IMMEDIATE ACTION REQUIRED: Critical security vulnerabilities detected",
                "Review and remove all hardcoded sensitive data",
                "Implement proper secrets management",
                "Consider code review and security audit"
            ])
        elif risk_level == 'high':
            recommendations.extend([
                "🔴 HIGH PRIORITY: Significant security risks detected",
                "Replace hardcoded credentials with environment variables",
                "Implement proper data classification",
                "Review data handling practices"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "🟡 MEDIUM RISK: Some security concerns identified",
                "Review sensitive data handling",
                "Consider input validation improvements",
                "Update security documentation"
            ])
        elif risk_level == 'low':
            recommendations.extend([
                "🟢 LOW RISK: Minor security improvements needed",
                "Continue following security best practices",
                "Consider preventive measures",
                "Regular security reviews recommended"
            ])
        else:
            recommendations.extend([
                "✅ MINIMAL RISK: Good security practices observed",
                "Continue current security approach",
                "Maintain regular security monitoring"
            ])
        
        # Category-specific recommendations
        if analysis_data.get('pii', 0) > 0:
            recommendations.append("Consider PII protection measures and compliance requirements")
        
        if analysis_data.get('medical', 0) > 0:
            recommendations.append("Ensure HIPAA compliance for medical data handling")
        
        if analysis_data.get('compliance_api', 0) > 0:
            recommendations.append("Review API security and credential management")
        
        return recommendations
    
    def compare_risks(self, analysis1: Dict, analysis2: Dict) -> Dict:
        """
        Compare two risk analyses
        
        Args:
            analysis1: First analysis data
            analysis2: Second analysis data
            
        Returns:
            Comparison analysis
        """
        risk1 = self.calculate_risk_score(analysis1)
        risk2 = self.calculate_risk_score(analysis2)
        
        score_diff = risk1['risk_score'] - risk2['risk_score']
        
        comparison = {
            'score_difference': score_diff,
            'risk_change': 'increased' if score_diff > 0 else 'decreased' if score_diff < 0 else 'no change',
            'analysis1_score': risk1['risk_score'],
            'analysis2_score': risk2['risk_score'],
            'analysis1_level': risk1['risk_level'],
            'analysis2_level': risk2['risk_level'],
            'significant_change': abs(score_diff) > 10,
            'improvement_recommendations': self._get_comparison_recommendations(risk1, risk2)
        }
        
        return compar
    
    def _get_comparison_recommendations(self, risk1: Dict, risk2: Dict) -> List[str]:
        """Get recommendations based on risk comparison"""
        recommendations = []
        
        delta = risk1['risk_score'] - risk2['risk_score']
        
        if delta > 10:
            recommendations.append("Significant risk increase detected - review recent changes")
        elif delta > 0:
            recommendations.append("Minor risk increase - monitor trends")
        elif delta < -10:
            recommendations.append("Significant risk improvement detected - continue good practices")
        elif delta < 0:
            recommendations.append("Minor risk improvement - maintain current approach")
        
        return recommendations
