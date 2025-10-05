# 🛡️ Sec360 - Advanced Code Security Analysis Platform

[![Cross-Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-blue)](https://github.com/yourusername/sec360)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green)](https://python.org)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20Powered-orange)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> **Sec360** is an advanced code security analysis platform that leverages AI-powered analysis to detect sensitive data exposure, security vulnerabilities, and compliance issues in your codebase. Built with Python and powered by Ollama's local LLM capabilities.

## 🎯 **Mission Statement**

Sec360 empowers developers to identify and mitigate security risks in their code before they become vulnerabilities. By combining automated analysis with AI-powered insights, we help teams maintain secure coding practices and protect sensitive data.

## ⭐ **Key Features**

### 🔒 **Practice Sessions**
- **Real-time code analysis** with Ollama AI integration
- **Security mentoring** focused on LLM data protection
- **Risk scoring** (0-100 scale) with detailed metrics
- **Duplicate code detection** to track analysis patterns
- **Session persistence** with automatic resume capability
- **Stop button functionality** to interrupt AI responses
- **Session timer** with auto-timeout (5 minutes default)
- **User session management** (one active session per user)

### 📊 **Analysis Engine**
- **Lines of Code** tracking and analysis
- **Sensitive Fields** identification and counting
- **Sensitive Data** detection and classification
- **PII (Personal Information)** detection
- **Medical Records** analysis (HIPAA compliance)
- **HEPA/Healthcare Data** analysis
- **Compliance/API** security validation
- **Risk Assessment** with detailed recommendations
- **Token usage tracking** for cost management

### 🏆 **Live Scoreboard**
- **Real-time performance tracking** across all users
- **Competitive rankings** with points system
- **Session statistics** and completion rates
- **Risk score monitoring** and trends
- **User progress visualization**

### 🔧 **Management Tools**
- **Cross-platform startup scripts** (macOS, Windows, Linux)
- **Automatic dependency installation**
- **Ollama integration** with model management
- **Session logging** and audit trails
- **Configuration management**

## 🚀 **Quick Start**

### **Prerequisites**
- **Python 3.8+**
- **Git** (for cloning)
- **Internet connection** (for initial setup)

### **One-Command Installation & Setup**

```bash
# Clone the repository
git clone https://github.com/yourusername/sec360.git
cd sec360

# Make scripts executable (Unix/macOS)
chmod +x scripts/management/start.sh
chmod +x scripts/management/stop.sh

# Start Sec360 (handles all dependencies automatically)
./scripts/management/start.sh
```

**That's it!** The start script will automatically:
- ✅ Detect your operating system
- ✅ Install missing dependencies (Homebrew, Ollama, Python packages)
- ✅ Download the required AI model (`llama3.2:3b`)
- ✅ Start all services
- ✅ Launch the Sec360 application

## 🖥️ **Platform-Specific Setup**

### **macOS Setup**
```bash
# The start script will automatically:
# 1. Install Homebrew (if not present)
# 2. Install Ollama via Homebrew
# 3. Configure shell environment
# 4. Download AI models
# 5. Start services

./scripts/management/start.sh
```

### **Windows Setup**
```bash
# The start script will automatically:
# 1. Detect Windows environment
# 2. Install Ollama via Chocolatey/Winget
# 3. Configure Python environment
# 4. Download AI models
# 5. Start services

# Run in PowerShell or Command Prompt
scripts\management\start.sh
```

### **Linux Setup**
```bash
# The start script will automatically:
# 1. Detect Linux distribution
# 2. Use appropriate package manager (apt/dnf/yum/zypper)
# 3. Install Ollama and dependencies
# 4. Configure environment
# 5. Start services

./scripts/management/start.sh
```

## 🤖 **LLM Integration & AI Assistance**

### **For AI Assistants Helping Users**

If you're an AI assistant helping users set up Sec360, here's what you need to know:

#### **System Architecture**
```
Sec360 Application
├── Core Analysis Engine (Python)
├── Ollama LLM Integration (Local AI)
├── Tkinter GUI Interface
├── Session Management System
└── Cross-Platform Scripts
```

#### **Key Components**
- **`sec360.py`** - Main application entry point
- **`core/analysis/ollama_analyzer.py`** - AI analysis engine
- **`core/practice_session_manager.py`** - Session and user management
- **`scripts/management/start.sh`** - Cross-platform startup script
- **`scripts/management/stop.sh`** - Clean shutdown script

#### **Dependencies**
```bash
# Python packages (auto-installed by start.sh)
requests>=2.31.0
psutil>=5.9.0
tkinter  # Usually built-in

# System dependencies (auto-installed by start.sh)
curl      # For downloading Ollama
git       # For repository cloning
Homebrew  # macOS package manager
Chocolatey/Winget  # Windows package managers
apt/dnf/yum/zypper  # Linux package managers
```

#### **Installation Troubleshooting**
```bash
# If Ollama installation fails:
# 1. Check internet connection
# 2. Verify system permissions
# 3. Try manual Ollama installation
# 4. Restart terminal after installation

# If Python dependencies fail:
pip install --upgrade pip
pip install requests psutil

# If GUI doesn't start:
# Check if tkinter is installed:
python3 -c "import tkinter; print('Tkinter OK')"
```

#### **Common Issues & Solutions**
- **"Ollama not found"** → Run `./scripts/setup/configure_shell.sh`
- **"Permission denied"** → Run `chmod +x scripts/management/*.sh`
- **"Model not found"** → Run `ollama pull llama3.2:3b`
- **"Port 11434 in use"** → Run `./scripts/management/stop.sh` then restart

## 📖 **Usage Guide**

### **Starting a Practice Session**

1. **Launch Sec360**
   ```bash
   ./scripts/management/start.sh
   ```

2. **Create New Session**
   - Enter your user ID
   - Select model (`llama3.2:3b` recommended)
   - Click "Start Session"

3. **Analyze Code**
   - Paste your code in the chat
   - Get real-time security analysis
   - Review risk scores and recommendations

### **Code Analysis Examples**

#### **Example 1: API Key Detection**
```python
# Input code
api_key = "sk-1234567890abcdef"
database_url = "postgresql://user:password@localhost:5432/db"

# Sec360 Analysis Output:
# 📊 Lines of Code: 2
# 🔍 Sensitive Fields: 2
# ⚠️ Sensitive Data: 2
# 🚨 Risk Score: 85/100 (HIGH RISK)
```

#### **Example 2: Medical Data Analysis**
```python
# Input code
patient_data = {
    "ssn": "123-45-6789",
    "diagnosis": "Type 2 Diabetes",
    "medications": ["Metformin", "Insulin"]
}

# Sec360 Analysis Output:
# 📊 Lines of Code: 4
# 🔍 Sensitive Fields: 3
# ⚠️ Sensitive Data: 3
# 🏥 Medical Data: 2
# 🚨 Risk Score: 92/100 (CRITICAL RISK)
```

### **Viewing Live Scoreboard**

```bash
# Open scoreboard in separate window
python3 scoreboard_launcher.py
```

## 🛠️ **Development**

### **Project Structure**
```
sec360/
├── core/                    # Core application logic
│   ├── analysis/           # Analysis engines
│   ├── detection/          # Data leak detection
│   ├── llm/               # Ollama integration
│   ├── logging_system/    # Logging and monitoring
│   ├── scoring/           # Scoring algorithms
│   └── session/          # Session management
├── scripts/               # Management scripts
│   ├── management/        # Start/stop/cleanup
│   └── setup/            # Configuration scripts
├── ui/                   # User interface components
├── data/                 # Sample data and templates
├── docs/                 # Documentation
├── tests/                # Test files
└── config/               # Configuration files
```

### **Running Tests**
```bash
# Run all tests
python3 -m pytest tests/

# Run specific test
python3 tests/test_table_parser.py
```

### **Contributing**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📊 **Performance Metrics**

- **Analysis Speed**: ~2-5 seconds per code snippet
- **Memory Usage**: ~200-500MB (including Ollama)
- **Supported Languages**: Python, JavaScript, Java, C++, and more
- **Model Size**: ~2GB (llama3.2:3b)
- **Concurrent Users**: Unlimited (local processing)

## 🔒 **Security Features**

- **Local Processing**: All analysis happens locally
- **No Data Transmission**: Code never leaves your machine
- **Encrypted Sessions**: Session data is encrypted
- **Audit Logging**: Complete analysis history
- **Access Control**: User-based session management

## 📈 **Roadmap**

- [ ] **Multi-language Support**: Enhanced language detection
- [ ] **Custom Models**: Support for custom Ollama models
- [ ] **Team Collaboration**: Multi-user analysis sessions
- [ ] **CI/CD Integration**: GitHub Actions and GitLab CI
- [ ] **API Endpoints**: REST API for programmatic access
- [ ] **Cloud Deployment**: Docker and Kubernetes support

## 🤝 **Support**

### **Getting Help**
- 📖 **Documentation**: Check the `docs/` folder
- 🐛 **Issues**: Report bugs on GitHub Issues
- 💬 **Discussions**: Join GitHub Discussions
- 📧 **Contact**: Reach out via GitHub profile

### **Troubleshooting**
```bash
# Check system status
./scripts/management/start.sh --status

# Reset configuration
./scripts/management/cleanup.sh

# View logs
tail -f logs/application.log
```

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Ollama Team** for the amazing local LLM platform
- **Python Community** for excellent libraries
- **Open Source Contributors** for inspiration and tools

---

**Made with ❤️ by Abhay**

*Empowering developers to write secure code, one analysis at a time.*