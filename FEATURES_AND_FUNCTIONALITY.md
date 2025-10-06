# 🛡️ **Sec360 by Abhay - Complete Feature & Functionality Documentation**

## 📋 **Application Overview**
**Sec360** is an advanced code security analysis platform designed to help developers practice secure coding and prevent sensitive data exposure when working with AI tools and Large Language Models (LLMs).

---

## 🎯 **Core Features & Functionality**

### **1. 🔒 Practice Sessions**
- **Real-time code analysis** with Ollama AI integration
- **Security mentoring** focused on LLM data protection
- **Risk scoring** (0-100 scale) with detailed metrics
- **Duplicate code detection** to track analysis patterns
- **Session persistence** with automatic resume capability
- **Stop button functionality** to interrupt AI responses
- **Session timer** with auto-timeout (5 minutes default)
- **User session management** (one active session per user)
- **Automatic detailed session creation** for comprehensive analysis
- **Enhanced risk viewer** with field/data breakdown and calculations

### **2. 📊 Analysis Engine**
- **Lines of Code** tracking and analysis
- **Sensitive Fields** identification and counting
- **Sensitive Data** detection and classification
- **PII (Personal Information)** detection
- **Medical Records** analysis (HIPAA compliance)
- **HEPA/Healthcare Data** analysis
- **Compliance/API** security validation
- **Risk Assessment** with detailed recommendations
- **Token usage tracking** for cost management

### **3. 🔍 Data Leak Detection**
- **API Key Detection**: API keys, access tokens, secret keys, bearer tokens
- **PII Detection**: SSN, credit cards, emails, phone numbers
- **Medical Data Detection**: Patient names, medical records, diagnoses, insurance IDs
- **Internal Infrastructure**: Hostnames, internal IPs, session IDs
- **Compliance Keywords**: GDPR, HIPAA, SOX, PCI-DSS related terms
- **Two-tier Detection System**:
  - **Tier 1**: Potential flags (all sensitive fields regardless of value)
  - **Tier 2**: Detected flags (only fields with actual sensitive data)

### **4. 📈 Scoring System**
- **Points-based ranking** system (0-100 scale)
- **Flag-based penalties** with different weights:
  - API_KEY: 15 points
  - TOKEN: 15 points
  - PASSWORD: 12 points
  - SSN: 12 points
  - CREDIT_CARD: 12 points
  - EMAIL: 8 points
  - PHONE: 8 points
  - MEDICAL: 10 points
  - PII: 12 points
  - GDPR: 8 points
  - COMPLIANCE: 5 points
  - HOSTNAME: 8 points
  - INTERNAL_IP: 8 points
  - SESSION_ID: 6 points
- **Performance levels**: Excellent (90+), Good (80+), Fair (70+), Poor (60+), Critical (<60)
- **User profile tracking** with session history
- **Improvement area identification**

### **5. 🎮 User Interface Components**

#### **Main Tabs:**
1. **🎯 Practice Session Tab**
   - User input field with send/stop/clear buttons
   - Model selection (static: llama3.2:3b)
   - Session information display (6-line textbox)
   - Chat display with AI Security Mentor (Arial 12pt font)
   - Real-time session metrics
   - Session timer display

2. **📝 Sample Code Tab**
   - Original samples (high sensitive data count)
   - Cleaned samples (minimal sensitive data count)
   - Comparison testing capabilities
   - Auto-loading into practice sessions

3. **📋 Session Logs Tab**
   - Session history browsing
   - Detailed analysis logs
   - Export capabilities for reports
   - Search and filter functionality
   - Risk Score Details viewer
   - Enhanced Log Viewer with conversations

4. **📊 Statistics Tab**
   - User performance tracking
   - Session statistics summary
   - Risk-based scoring algorithms
   - Metrics visualization

5. **👥 Active Sessions Tab**
   - Real-time session monitoring
   - User session management
   - Session status tracking

6. **📖 Analysis History Tab**
   - Complete analysis history
   - Historical data review
   - Trend analysis

7. **⚙️ System Status Tab**
   - Ollama service status
   - System health monitoring
   - Configuration display

---

## 🔧 **Technical Architecture**

### **Core Components:**

#### **1. Analysis Engine (`core/analysis/`)**
- **`ollama_analyzer.py`**: AI-powered code analysis using Ollama
- **`json_parser.py`**: Structured data parsing
- **`risk_calculator.py`**: Risk scoring algorithms
- **`simple_parser.py`**: Basic text parsing utilities

#### **2. Detection System (`core/detection/`)**
- **`data_monitor.py`**: Real-time sensitive data detection
- **Pattern-based detection** using regex
- **Confidence scoring** for flagged content
- **Deduplication** to prevent false positives

#### **3. LLM Integration (`core/llm/`)**
- **`ollama_client.py`**: Ollama API integration
- **`mac_silicon_optimizer.py`**: Mac Silicon performance optimization
- **Model management** and switching
- **Token usage tracking**

#### **4. Session Management (`core/practice_session_manager.py`)**
- **Session lifecycle** management
- **User session tracking**
- **Duplicate detection** and prevention
- **Metrics collection** and storage
- **Timer management**

#### **5. Scoring System (`core/scoring/`)**
- **`scoring_system.py`**: Comprehensive scoring algorithms
- **User profile management**
- **Session score calculation**
- **Leaderboard functionality**

#### **6. Logging System (`core/logging_system/`)**
- **`log_viewer.py`**: Risk Score Details viewer with calculation breakdown
- **`detailed_log_viewer.py`**: Enhanced log viewer with conversations
- **Session log storage**
- **Analysis history tracking**
- **Automatic detailed session file creation**

#### **7. Scoreboard (`core/scoreboard/`)**
- **`scoreboard_viewer.py`**: Performance tracking UI
- **User rankings**
- **Statistics display**

---

## 🚀 **Management Scripts**

### **1. Start Script (`scripts/management/start.sh`)**
- **Cross-platform Ollama installation** (macOS, Linux, Windows)
- **Automatic Homebrew installation** on macOS
- **Shell environment configuration**
- **Dependency management** (Python packages)
- **Service startup** and verification
- **Model installation** and management
- **Clean startup** with process cleanup

### **2. Stop Script (`scripts/management/stop.sh`)**
- **Graceful service shutdown**
- **Process cleanup**
- **Port management**
- **Log management** (optional cleanup)

### **3. Cleanup Script (`scripts/management/cleanup.sh`)**
- **Session file cleanup**
- **Detailed session file cleanup**
- **Process termination**
- **Log management**

### **4. Uninstall Script (`scripts/management/uninstall.sh`)**
- **Complete dependency removal**
- **Python package uninstallation**
- **Ollama removal**
- **Shell configuration cleanup**
- **File cleanup**

### **5. Shell Configuration (`scripts/setup/configure_shell.sh`)**
- **Shell detection** (zsh, bash, fish)
- **PATH configuration** for Homebrew
- **Environment variable setup**
- **Configuration backup**

---

## 📊 **Data Management**

### **Sample Data (`data/`)**
- **API Keys Sample**: High-risk API key examples
- **Compliance Sample**: Compliance-related code
- **Internal Infrastructure Sample**: Internal system code
- **Medical Records Sample**: HIPAA-related data
- **PII Sample**: Personal information examples
- **Cleaned Versions**: Sanitized versions for comparison

### **Configuration Files**
- **`config.json`**: Main application configuration
- **`core/monitor_config.json`**: Detection pattern configuration
- **`core/scoring_config.json`**: Scoring system configuration
- **`core/mac_silicon_config.json`**: Mac Silicon optimization settings

---

## 🔒 **Security Features**

### **Detection Patterns**
- **API Keys**: 20+ character alphanumeric patterns
- **Tokens**: Bearer tokens, access tokens
- **Passwords**: Password field detection
- **SSN**: Social Security Number patterns
- **Credit Cards**: Credit card number patterns
- **Emails**: Email address validation
- **Phone Numbers**: Phone number patterns
- **Medical Data**: Patient names, diagnoses, medical records
- **Internal Systems**: Hostnames, IP addresses, session IDs

### **Risk Assessment**
- **Multi-factor risk calculation**
- **Category-based risk weighting**
- **Confidence scoring**
- **Threshold-based risk levels**

---

## 📈 **Performance Features**

### **Optimization**
- **Mac Silicon optimization** for Apple M1/M2 chips
- **Caching system** for analysis results
- **Deduplication** to prevent redundant analysis
- **Token usage optimization**
- **Memory management**

### **Monitoring**
- **Real-time metrics** tracking
- **Performance monitoring**
- **Resource usage tracking**
- **Session analytics**

---

## 🎯 **Key Functions & Methods**

### **Main Application (`sec360.py`)**
- `setup_ui()`: UI initialization
- `setup_practice_tab()`: Practice session setup
- `check_ollama_status()`: Service status checking
- `load_existing_active_sessions()`: Session restoration

### **Practice Session Manager**
- `start_session()`: Session initialization
- `end_session()`: Session termination
- `send_message()`: Message processing
- `stop_thinking_process()`: AI response interruption
- `_track_code_analysis()`: Duplicate detection
- `_show_thinking_indicator()`: UI feedback
- `_clear_thinking_indicator()`: UI cleanup

### **Data Monitor**
- `analyze_input()`: Input analysis
- `_check_patterns()`: Pattern matching
- `_count_potential_flags()`: Flag counting
- `_is_code_like_input()`: Code detection

### **Scoring System**
- `calculate_session_score()`: Score calculation
- `get_user_profile()`: Profile retrieval
- `get_leaderboard()`: Ranking system
- `_identify_improvement_areas()`: Improvement suggestions

---

## 🌟 **Unique Features**

1. **AI-Powered Security Mentoring**: Real-time guidance on secure coding practices
2. **LLM Data Protection Focus**: Specifically designed to prevent sensitive data exposure to AI tools
3. **Comprehensive Risk Assessment**: Multi-dimensional risk scoring system
4. **Cross-Platform Compatibility**: Works on macOS, Linux, and Windows
5. **Real-Time Analysis**: Instant feedback on code security
6. **Session Persistence**: Automatic session recovery and management
7. **Duplicate Detection**: Prevents redundant analysis
8. **Token Management**: Cost-effective AI usage tracking
9. **Performance Optimization**: Mac Silicon specific optimizations
10. **Comprehensive Logging**: Detailed analysis history and reporting

---

## 📋 **Dependencies**

### **Python Dependencies (`requirements.txt`)**
- **requests>=2.31.0**: HTTP client for API calls
- **psutil>=5.9.0**: System and process monitoring
- **numpy>=1.24.0**: Numerical computing (Mac Silicon optimized)
- **scipy>=1.10.0**: Scientific computing (Mac Silicon optimized)

### **System Requirements**
- **Python 3.11+**: Required for Ollama integration
- **Ollama AI Platform**: Local LLM service
- **llama3.2:3b Model**: Primary AI model for analysis
- **8GB+ RAM**: Recommended for optimal performance
- **macOS 12+**: Tested compatibility (cross-platform support)

---

## 🚀 **Quick Start Guide**

### **1. Installation**
```bash
# Start the application with automatic setup
./scripts/management/start.sh
```

### **2. Usage**
1. **Launch Application**: Run the start script
2. **Access Practice Sessions**: Navigate to Practice Session tab
3. **Start Session**: Enter username and begin coding
4. **Get Analysis**: Submit code for security analysis
5. **Review Results**: Check risk scores and recommendations
6. **Track Progress**: Monitor statistics and improvements

### **3. Management**
```bash
# Stop the application
./scripts/management/stop.sh

# Clean up sessions
./scripts/management/cleanup.sh

# Uninstall everything
./scripts/management/uninstall.sh
```

---

## 📊 **Analysis Metrics**

### **Code Analysis Output**
| Metric | Description | Example |
|--------|-------------|---------|
| Lines of Code | Total lines analyzed | 42 |
| Sensitive Fields | Variables holding sensitive data | 3 |
| Sensitive Data | Actual sensitive values found | 2 |
| PII Count | Personally identifiable information | 1 |
| HEPA Count | Healthcare data | 0 |
| Medical Count | HIPAA-regulated data | 1 |
| Compliance/API | Security credentials | 1 |
| Risk Score | 0-100 calculated risk level | 84 |

### **Risk Levels**
- **Low Risk**: 0-30 (Minimal sensitive data)
- **Medium Risk**: 31-60 (Moderate sensitive data)
- **High Risk**: 61-80 (Significant sensitive data)
- **Critical Risk**: 81-100 (Extensive sensitive data)

---

## 🔧 **Configuration Options**

### **Application Settings (`config.json`)**
```json
{
  "core_settings": {
    "ollama_url": "http://localhost:11434",
    "default_model": "llama3.2:3b",
    "analysis_timeout": 30
  },
  "risk_scoring": {
    "weights": {
      "lines_weight": 0.1,
      "fields_weight": 0.3,
      "data_weight": 0.4,
      "category_weight": 0.2
    }
  },
  "ui_settings": {
    "window_width": 1400,
    "window_height": 900,
    "font_family": "Consolas",
    "font_size": 10
  }
}
```

---

## 📝 **Logging & Monitoring**

### **Log Files**
- **`logs/application.log`**: Main application logs
- **`logs/ollama.log`**: Ollama service logs
- **`core/logs/sessions/`**: Session-specific logs
- **`core/logs/data_monitor.log`**: Detection logs

### **Monitoring Features**
- **Real-time status** monitoring
- **Service health** checks
- **Performance metrics** tracking
- **Error logging** and reporting

---

## 🎯 **Best Practices**

### **For Developers**
1. **Regular Practice**: Use the platform regularly to improve security awareness
2. **Review Analysis**: Pay attention to risk scores and recommendations
3. **Learn Patterns**: Understand common sensitive data patterns
4. **Sanitize Code**: Practice removing sensitive data before sharing with AI tools
5. **Track Progress**: Monitor improvement over time

### **For Organizations**
1. **Team Training**: Use for team security training sessions
2. **Code Review**: Integrate into code review processes
3. **Compliance**: Ensure HIPAA, GDPR, and other compliance requirements
4. **Risk Assessment**: Regular security risk evaluations
5. **Documentation**: Maintain security analysis records

---

## 🔮 **Future Enhancements**

### **Planned Features**
- **Additional AI Models**: Support for more LLM models
- **Custom Patterns**: User-defined detection patterns
- **Team Collaboration**: Multi-user session support
- **API Integration**: REST API for external integrations
- **Advanced Analytics**: Machine learning-based risk prediction
- **Cloud Deployment**: Cloud-based analysis capabilities

---

## 📞 **Support & Documentation**

### **Additional Resources**
- **`README.md`**: Basic project overview
- **`HOW_TO_RUN.md`**: Detailed setup instructions
- **`docs/FINAL_TEST.md`**: Testing and validation results
- **`docs/ENABLE_ANALYSIS_TAB.md`**: Advanced analysis features

### **Troubleshooting**
- **Check Ollama Status**: Ensure Ollama service is running
- **Verify Dependencies**: Run dependency checks
- **Review Logs**: Check application and Ollama logs
- **Restart Services**: Use stop/start scripts for clean restart

---

**Sec360 by Abhay** - Empowering developers with AI-powered security analysis and secure coding practices.

## 🆕 **Recent Updates**

### **v2.1.0 - Enhanced Analysis & Risk Viewer**
- ✅ **Automatic detailed session creation** - Sessions now automatically generate comprehensive analysis files
- ✅ **Enhanced risk viewer** - Complete breakdown of field/data calculations with multipliers
- ✅ **Improved session management** - Better handling of session end scenarios
- ✅ **Enhanced debugging** - Comprehensive logging for troubleshooting
- ✅ **Cross-platform compatibility** - All features work seamlessly across macOS, Windows, and Linux

### **Key Improvements**
- **Risk Score Details Viewer**: Now displays accurate field counts, data points, and calculation breakdowns
- **Category Breakdown**: Shows PII, Medical, HEPA, and API/Security data with individual multipliers
- **Session Persistence**: Enhanced session file creation for both regular and detailed analysis
- **Management Scripts**: Updated cleanup and deletion scripts to handle new file structures

---

*Last Updated: October 2025*
