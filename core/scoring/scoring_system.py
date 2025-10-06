#!/usr/bin/env python3
"""
Scoring System for LLM Safety Training
Calculates and tracks user scores based on flagged content
"""

import json
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import os

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
class SessionScore:
    session_id: str
    user_id: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    total_flags: int
    score: float
    flag_breakdown: Dict[str, int]
    confidence_scores: List[float]
    sample_files_used: List[str]
    improvement_areas: List[str]

@dataclass
class UserProfile:
    user_id: str
    total_sessions: int
    average_score: float
    best_score: float
    worst_score: float
    total_flags: int
    flag_history: Dict[str, int]
    improvement_trend: float
    last_session_date: datetime.datetime

class ScoringSystem:
    def __init__(self, config_file: str = "core/scoring_config.json"):
        self.config = self._load_config(config_file)
        self.scores_file = "core/logs/user_scores.json"
        self.profiles_file = "core/logs/user_profiles.json"
        self.scores = self._load_scores()
        self.profiles = self._load_profiles()
        
    def _load_config(self, config_file: str) -> Dict:
        """Load scoring configuration"""
        default_config = {
            "penalties": {
                "API_KEY": 15,
                "TOKEN": 15,
                "PASSWORD": 12,
                "SSN": 12,
                "CREDIT_CARD": 12,
                "EMAIL": 8,
                "PHONE": 8,
                "MEDICAL": 10,
                "PII": 12,
                "GDPR": 8,
                "COMPLIANCE": 5,
                "HOSTNAME": 8,
                "INTERNAL_IP": 8,
                "SESSION_ID": 6
            },
            "base_score": 100,
            "confidence_multiplier": 1.0,
            "improvement_threshold": 0.1,
            "levels": {
                "excellent": 90,
                "good": 80,
                "fair": 70,
                "poor": 60,
                "critical": 0
            }
        }
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default_config
    
    def _load_scores(self) -> List[SessionScore]:
        """Load existing scores from file"""
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    data = json.load(f)
                    scores = []
                    for item in data:
                        # Convert datetime strings back to datetime objects
                        item['start_time'] = datetime.datetime.fromisoformat(item['start_time'])
                        item['end_time'] = datetime.datetime.fromisoformat(item['end_time'])
                        scores.append(SessionScore(**item))
                    return scores
            except Exception as e:
                print(f"Error loading scores: {e}")
        return []
    
    def _load_profiles(self) -> Dict[str, UserProfile]:
        """Load user profiles from file"""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    profiles = {}
                    for user_id, profile_data in data.items():
                        profile_data['last_session_date'] = datetime.datetime.fromisoformat(profile_data['last_session_date'])
                        profiles[user_id] = UserProfile(**profile_data)
                    return profiles
            except Exception as e:
                print(f"Error loading profiles: {e}")
        return {}
    
    def _save_scores(self):
        """Save scores to file"""
        try:
            with open(self.scores_file, 'w') as f:
                json.dump([asdict(score) for score in self.scores], f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving scores: {e}")
    
    def _save_profiles(self):
        """Save user profiles to file"""
        try:
            with open(self.profiles_file, 'w') as f:
                data = {}
                for user_id, profile in self.profiles.items():
                    data[user_id] = asdict(profile)
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    def calculate_session_score(self, session_logs: List[Dict], user_id: str, sample_files: List[str] = None) -> SessionScore:
        """Calculate score for a session"""
        if not session_logs:
            return SessionScore(
                session_id="empty_session",
                user_id=user_id,
                start_time=datetime.datetime.now(),
                end_time=datetime.datetime.now(),
                total_flags=0,
                score=100.0,
                flag_breakdown={},
                confidence_scores=[],
                sample_files_used=sample_files or [],
                improvement_areas=[]
            )
        
        # Calculate score
        score = self.config["base_score"]
        flag_breakdown = {}
        confidence_scores = []
        
        for log in session_logs:
            flag_type = log["flag_type"]
            confidence = log["confidence"]
            
            # Count flags by type
            flag_breakdown[flag_type] = flag_breakdown.get(flag_type, 0) + 1
            
            # Apply penalty
            penalty = self.config["penalties"].get(flag_type, 5)
            score -= penalty * confidence * self.config["confidence_multiplier"]
            
            confidence_scores.append(confidence)
        
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        # Determine improvement areas
        improvement_areas = self._identify_improvement_areas(flag_breakdown)
        
        # Find actual session start and end times
        session_start_time = None
        session_end_time = None
        
        # Look for session start/end logs
        for log in session_logs:
            content = log.get('content', '').lower()
            if 'session started' in content or 'practice session started' in content:
                session_start_time = datetime.datetime.fromisoformat(log['timestamp'])
            elif 'session ended' in content or 'session completed' in content:
                session_end_time = datetime.datetime.fromisoformat(log['timestamp'])
        
        # Fallback to first and last log timestamps
        if not session_start_time:
            session_start_time = datetime.datetime.fromisoformat(session_logs[0]["timestamp"])
        if not session_end_time:
            session_end_time = datetime.datetime.fromisoformat(session_logs[-1]["timestamp"])
        
        # Create session score
        session_score = SessionScore(
            session_id=session_logs[0]["session_id"],
            user_id=user_id,
            start_time=session_start_time,
            end_time=session_end_time,
            total_flags=len(session_logs),
            score=score,
            flag_breakdown=flag_breakdown,
            confidence_scores=confidence_scores,
            sample_files_used=sample_files or [],
            improvement_areas=improvement_areas
        )
        
        # Save score
        self.scores.append(session_score)
        self._save_scores()
        
        # Update user profile
        self._update_user_profile(session_score)
        
        return session_score
    
    def _identify_improvement_areas(self, flag_breakdown: Dict[str, int]) -> List[str]:
        """Identify areas for improvement based on flag types"""
        improvement_areas = []
        
        if flag_breakdown.get("API_KEY", 0) > 0:
            improvement_areas.append("Avoid sharing API keys and tokens")
        
        if flag_breakdown.get("PII", 0) > 0:
            improvement_areas.append("Protect personal identifiable information")
        
        if flag_breakdown.get("MEDICAL", 0) > 0:
            improvement_areas.append("Never share medical records or health information")
        
        if flag_breakdown.get("HOSTNAME", 0) > 0:
            improvement_areas.append("Keep internal infrastructure details private")
        
        if flag_breakdown.get("COMPLIANCE", 0) > 0:
            improvement_areas.append("Be aware of compliance and regulatory requirements")
        
        return improvement_areas
    
    def _update_user_profile(self, session_score: SessionScore):
        """Update user profile with new session data"""
        user_id = session_score.user_id
        
        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile(
                user_id=user_id,
                total_sessions=0,
                average_score=0.0,
                best_score=0.0,
                worst_score=100.0,
                total_flags=0,
                flag_history={},
                improvement_trend=0.0,
                last_session_date=session_score.start_time
            )
        
        profile = self.profiles[user_id]
        
        # Update basic stats
        profile.total_sessions += 1
        profile.total_flags += session_score.total_flags
        profile.last_session_date = session_score.start_time
        
        # Update scores
        if session_score.score > profile.best_score:
            profile.best_score = session_score.score
        
        if session_score.score < profile.worst_score:
            profile.worst_score = session_score.score
        
        # Calculate average score
        total_score = sum(score.score for score in self.scores if score.user_id == user_id)
        profile.average_score = total_score / profile.total_sessions
        
        # Update flag history
        for flag_type, count in session_score.flag_breakdown.items():
            profile.flag_history[flag_type] = profile.flag_history.get(flag_type, 0) + count
        
        # Calculate improvement trend
        user_scores = [score.score for score in self.scores if score.user_id == user_id]
        if len(user_scores) >= 2:
            recent_avg = sum(user_scores[-3:]) / min(3, len(user_scores))
            older_avg = sum(user_scores[:-3]) / max(1, len(user_scores) - 3) if len(user_scores) > 3 else recent_avg
            profile.improvement_trend = recent_avg - older_avg
        
        self._save_profiles()
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        return self.profiles.get(user_id)
    
    def get_user_scores(self, user_id: str) -> List[SessionScore]:
        """Get all scores for a user"""
        return [score for score in self.scores if score.user_id == user_id]
    
    def get_score_level(self, score: float) -> str:
        """Get score level based on score value"""
        levels = self.config["levels"]
        
        if score >= levels["excellent"]:
            return "Excellent"
        elif score >= levels["good"]:
            return "Good"
        elif score >= levels["fair"]:
            return "Fair"
        elif score >= levels["poor"]:
            return "Poor"
        else:
            return "Critical"
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get leaderboard of users by average score"""
        leaderboard = []
        
        for user_id, profile in self.profiles.items():
            if profile.total_sessions >= 3:  # Only include users with at least 3 sessions
                leaderboard.append({
                    "user_id": user_id,
                    "average_score": profile.average_score,
                    "total_sessions": profile.total_sessions,
                    "best_score": profile.best_score,
                    "improvement_trend": profile.improvement_trend
                })
        
        # Sort by average score descending
        leaderboard.sort(key=lambda x: x["average_score"], reverse=True)
        
        return leaderboard[:limit]
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        if not self.scores:
            return {"message": "No scores available"}
        
        total_sessions = len(self.scores)
        total_users = len(self.profiles)
        average_score = sum(score.score for score in self.scores) / total_sessions
        
        # Score distribution
        score_distribution = {}
        for score in self.scores:
            level = self.get_score_level(score.score)
            score_distribution[level] = score_distribution.get(level, 0) + 1
        
        # Most common flag types
        flag_counts = {}
        for score in self.scores:
            for flag_type, count in score.flag_breakdown.items():
                flag_counts[flag_type] = flag_counts.get(flag_type, 0) + count
        
        most_common_flags = sorted(flag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_sessions": total_sessions,
            "total_users": total_users,
            "average_score": average_score,
            "score_distribution": score_distribution,
            "most_common_flags": most_common_flags,
            "best_overall_score": max(score.score for score in self.scores),
            "worst_overall_score": min(score.score for score in self.scores)
        }

if __name__ == "__main__":
    # Test the scoring system
    scoring_system = ScoringSystem()
    
    # Sample session logs
    sample_logs = [
        {
            "session_id": "test_session_1",
            "timestamp": "2024-01-15T10:00:00",
            "flag_type": "API_KEY",
            "confidence": 0.9
        },
        {
            "session_id": "test_session_1",
            "timestamp": "2024-01-15T10:05:00",
            "flag_type": "PII",
            "confidence": 0.8
        }
    ]
    
    # Calculate score
    session_score = scoring_system.calculate_session_score(sample_logs, "test_user", ["api_keys_sample.py"])
    
    print(f"Session Score: {session_score.score:.1f}")
    print(f"Total Flags: {session_score.total_flags}")
    print(f"Improvement Areas: {session_score.improvement_areas}")
    
    # Get statistics
    stats = scoring_system.get_statistics()
    print(f"\nStatistics: {stats}")
