#!/bin/bash

# Sec360 by Abhay - Advanced Code Security Analysis Platform - Start Script
# This script starts all required services with clean startup

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local process_name=$2
    
    print_status "Checking for processes on port $port..."
    
    # Find processes using the port
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        print_warning "Found processes on port $port: $pids"
        for pid in $pids; do
            print_status "Killing process $pid on port $port"
            kill -9 $pid 2>/dev/null || true
        done
        sleep 2
        print_success "Cleared port $port"
    else
        print_status "Port $port is free"
    fi
}

# Function to kill processes by name
kill_process() {
    local process_name=$1
    local signal=${2:-TERM}
    
    print_status "Checking for $process_name processes..."
    
    local pids=$(pgrep -f "$process_name" 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        print_warning "Found $process_name processes: $pids"
        for pid in $pids; do
            print_status "Killing $process_name process $pid"
            kill -$signal $pid 2>/dev/null || true
        done
        sleep 2
        
        # Force kill if still running
        local remaining_pids=$(pgrep -f "$process_name" 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            print_warning "Force killing remaining $process_name processes: $remaining_pids"
            for pid in $remaining_pids; do
                kill -9 $pid 2>/dev/null || true
            done
        fi
        print_success "Cleared $process_name processes"
    else
        print_status "No $process_name processes found"
    fi
}

# Function to stop Docker containers
stop_containers() {
    print_status "Checking for Docker containers..."
    
    if command_exists docker; then
        # Stop all running containers
        local containers=$(docker ps -q 2>/dev/null || true)
        if [ -n "$containers" ]; then
            print_warning "Found running Docker containers: $containers"
            docker stop $containers 2>/dev/null || true
            print_success "Stopped Docker containers"
        else
            print_status "No running Docker containers found"
        fi
        
        # Remove stopped containers
        local stopped_containers=$(docker ps -aq 2>/dev/null || true)
        if [ -n "$stopped_containers" ]; then
            print_status "Removing stopped containers..."
            docker rm $stopped_containers 2>/dev/null || true
            print_success "Removed stopped containers"
        fi
    else
        print_status "Docker not found, skipping container cleanup"
    fi
}

# Function to clean up Python processes
cleanup_tkinter() {
    print_status "Cleaning up tkinter/GUI processes..."
    
    # Direct kill approach for log viewers
    pkill -f "core.logging_system.log_viewer" 2>/dev/null || true
    pkill -f "log_viewer" 2>/dev/null || true
    
    # Check if any tkinter-related processes remain
    local tkinter_pids=$(pgrep -f "core.logging_system.log_viewer\|log_viewer" 2>/dev/null || true)
    if [ -n "$tkinter_pids" ]; then
        print_warning "Found remaining tkinter processes: $tkinter_pids"
        for pid in $tkinter_pids; do
            print_status "Force killing tkinter process $pid"
            kill -9 $pid 2>/dev/null || true
        done
        sleep 1
        print_success "Cleared tkinter processes"
    else
        print_success "No tkinter processes found"
    fi
}

cleanup_python() {
    print_status "Cleaning up Python processes..."
    
    # First cleanup tkinter processes
    cleanup_tkinter
    
    # Kill Python processes related to our application
    local python_pids=$(pgrep -f "sec360\.py\|scoreboard_launcher\.py\|llm-safety-trainer\|log_viewer\.py\|core.logging_system.log_viewer" 2>/dev/null || true)
    if [ -n "$python_pids" ]; then
        print_warning "Found Python processes: $python_pids"
        for pid in $python_pids; do
            print_status "Killing Python process $pid"
            kill -TERM $pid 2>/dev/null || true
        done
        sleep 2
        
        # Force kill if still running
        local remaining_pids=$(pgrep -f "sec360\.py\|scoreboard_launcher\.py\|llm-safety-trainer\|log_viewer\.py\|core.logging_system.log_viewer" 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            for pid in $remaining_pids; do
                kill -9 $pid 2>/dev/null || true
            done
        fi
        print_success "Cleared Python processes"
    else
        print_status "No Python processes found"
    fi
}

# Function to check and configure Homebrew PATH
configure_homebrew_path() {
    # Check if Homebrew is installed but not in PATH
    if [[ -f "/opt/homebrew/bin/brew" ]] && ! command_exists brew; then
        # Apple Silicon Mac - add to PATH
        export PATH="/opt/homebrew/bin:$PATH"
        print_status "Configured Homebrew PATH for Apple Silicon Mac"
        return 0
    elif [[ -f "/usr/local/bin/brew" ]] && ! command_exists brew; then
        # Intel Mac - add to PATH
        export PATH="/usr/local/bin:$PATH"
        print_status "Configured Homebrew PATH for Intel Mac"
        return 0
    fi
    return 1
}

# Function to configure shell environment for Homebrew
configure_shell_environment() {
    local shell_config_file=""
    local homebrew_path=""
    
    # Detect shell and determine config file
    if [[ "$SHELL" == *"zsh"* ]]; then
        shell_config_file="$HOME/.zshrc"
        print_status "Detected Zsh shell"
    elif [[ "$SHELL" == *"bash"* ]]; then
        shell_config_file="$HOME/.bashrc"
        print_status "Detected Bash shell"
    else
        shell_config_file="$HOME/.profile"
        print_status "Using .profile as fallback"
    fi
    
    # Determine Homebrew path based on architecture
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        homebrew_path="/opt/homebrew/bin"
        print_status "Using Apple Silicon Homebrew path"
    elif [[ -f "/usr/local/bin/brew" ]]; then
        homebrew_path="/usr/local/bin"
        print_status "Using Intel Mac Homebrew path"
    else
        print_warning "Homebrew path not found"
        return 1
    fi
    
    # Check if Homebrew is already in the config file
    if [[ -f "$shell_config_file" ]] && grep -q "homebrew" "$shell_config_file" 2>/dev/null; then
        print_status "Homebrew already configured in $shell_config_file"
        return 0
    fi
    
    # Add Homebrew to shell config
    print_status "Adding Homebrew to $shell_config_file..."
    
    # Create backup of existing config
    if [[ -f "$shell_config_file" ]]; then
        cp "$shell_config_file" "${shell_config_file}.backup.$(date +%Y%m%d_%H%M%S)"
        print_status "Created backup of existing config"
    fi
    
    # Add Homebrew configuration
    cat >> "$shell_config_file" << EOF

# Homebrew configuration (added by Sec360)
export PATH="$homebrew_path:\$PATH"
export HOMEBREW_NO_AUTO_UPDATE=1
export HOMEBREW_NO_INSTALL_CLEANUP=1
EOF
    
    print_success "Homebrew configuration added to $shell_config_file"
    
    # Source the config file for current session
    if [[ -f "$shell_config_file" ]]; then
        print_status "Sourcing $shell_config_file for current session..."
        source "$shell_config_file" 2>/dev/null || true
        print_success "Shell environment configured"
    fi
    
    return 0
}

# Function to verify and start Ollama service
verify_and_start_ollama() {
    print_status "Verifying Ollama installation..."
    
    # Check if Ollama is in PATH
    if ! command_exists ollama; then
        print_warning "Ollama not found in PATH, trying to configure..."
        configure_shell_environment
        
        # Try again after configuration
        if ! command_exists ollama; then
            print_error "Ollama still not accessible after configuration"
            print_status "Please restart your terminal and run this script again"
            return 1
        fi
    fi
    
    # Verify Ollama version
    local ollama_version=$(ollama --version 2>&1 | grep -v "Warning" | head -n1)
    print_success "Ollama version: $ollama_version"
    
    # Check if Ollama service is running
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_success "Ollama service is already running"
        return 0
    fi
    
    # Start Ollama service
    print_status "Starting Ollama service..."
    if ollama serve > logs/ollama.log 2>&1 &
    then
        local ollama_pid=$!
        print_success "Ollama service started (PID: $ollama_pid)"
        echo $ollama_pid > logs/ollama.pid
        
        # Wait for service to be ready
        print_status "Waiting for Ollama service to be ready..."
        local max_attempts=30
        local attempt=0
        
        while [ $attempt -lt $max_attempts ]; do
            if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
                print_success "Ollama service is ready"
                return 0
            fi
            
            attempt=$((attempt + 1))
            sleep 1
            print_status "Attempt $attempt/$max_attempts - Waiting for Ollama..."
        done
        
        print_error "Ollama service failed to start properly"
        return 1
    else
        print_error "Failed to start Ollama service"
        return 1
    fi
}

# Function to install Homebrew on macOS
install_homebrew() {
    print_status "Installing Homebrew..."
    print_status "This may take a few minutes..."
    
    # Install Homebrew using the official installer
    if /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
        print_success "Homebrew installed successfully"
        
        # Configure shell environment for Homebrew
        if configure_shell_environment; then
            print_success "Homebrew is ready to use"
            return 0
        else
            print_warning "Homebrew installed but shell configuration failed"
            print_status "Please restart your terminal or run: source ~/.zshrc"
            return 1
        fi
    else
        print_error "Failed to install Homebrew"
        return 1
    fi
}

# Function to detect system information
detect_system() {
    local os_type=$(uname -s)
    local arch=$(uname -m)
    local os_name=""
    local package_manager=""
    local install_method=""
    
    case "$os_type" in
        "Darwin")
            os_name="macOS"
            if [[ "$arch" == "arm64" ]]; then
                arch="Apple Silicon"
            else
                arch="Intel"
            fi
            package_manager="Homebrew"
            install_method="homebrew"
            ;;
        "Linux")
            os_name="Linux"
            # Detect Linux distribution
            if [[ -f "/etc/os-release" ]]; then
                source /etc/os-release
                case "$ID" in
                    "ubuntu"|"debian")
                        package_manager="apt"
                        install_method="apt"
                        ;;
                    "fedora"|"rhel"|"centos")
                        package_manager="dnf/yum"
                        install_method="dnf"
                        ;;
                    "arch"|"manjaro")
                        package_manager="pacman"
                        install_method="pacman"
                        ;;
                    "opensuse"|"sles")
                        package_manager="zypper"
                        install_method="zypper"
                        ;;
                    *)
                        package_manager="unknown"
                        install_method="manual"
                        ;;
                esac
            else
                package_manager="unknown"
                install_method="manual"
            fi
            ;;
        "CYGWIN"*|"MINGW"*|"MSYS"*)
            os_name="Windows"
            arch="x86_64"
            package_manager="Chocolatey/Winget"
            install_method="windows"
            ;;
        *)
            os_name="Unknown"
            arch="unknown"
            package_manager="unknown"
            install_method="manual"
            ;;
    esac
    
    echo "$os_name|$arch|$package_manager|$install_method"
}

# Function to install Ollama on Windows
install_ollama_windows() {
    print_status "Installing Ollama on Windows..."
    
    # Check if Chocolatey is available
    if command_exists choco; then
        print_status "Installing Ollama via Chocolatey..."
        if choco install ollama -y; then
            print_success "Ollama installed successfully via Chocolatey"
            return 0
        else
            print_warning "Chocolatey installation failed, trying Winget..."
        fi
    fi
    
    # Check if Winget is available
    if command_exists winget; then
        print_status "Installing Ollama via Winget..."
        if winget install Ollama.Ollama; then
            print_success "Ollama installed successfully via Winget"
            return 0
        else
            print_warning "Winget installation failed, trying manual download..."
        fi
    fi
    
    # Manual download for Windows
    print_status "Downloading Ollama for Windows..."
    print_status "Please visit https://ollama.ai/download to download the Windows installer"
    
    # Try to open the download page
    if command_exists start; then
        print_status "Opening Ollama download page..."
        start "https://ollama.ai/download"
    fi
    
    print_error "Automatic installation not available for Windows"
    print_status "Please download and install Ollama manually from https://ollama.ai/download"
    return 1
}

# Function to install Ollama on Linux
install_ollama_linux() {
    local install_method=$1
    print_status "Installing Ollama on Linux using $install_method..."
    
    case "$install_method" in
        "apt")
            print_status "Installing Ollama via apt..."
            # Add Ollama repository
            curl -fsSL https://ollama.com/install.sh | sh
            ;;
        "dnf")
            print_status "Installing Ollama via dnf..."
            # Add Ollama repository
            curl -fsSL https://ollama.com/install.sh | sh
            ;;
        "pacman")
            print_status "Installing Ollama via pacman..."
            # Install from AUR or use official installer
            if command_exists yay; then
                yay -S ollama
            elif command_exists paru; then
                paru -S ollama
            else
                curl -fsSL https://ollama.com/install.sh | sh
            fi
            ;;
        "zypper")
            print_status "Installing Ollama via zypper..."
            curl -fsSL https://ollama.com/install.sh | sh
            ;;
        *)
            print_status "Using official installer script..."
            curl -fsSL https://ollama.com/install.sh | sh
            ;;
    esac
    
    if command_exists ollama; then
        print_success "Ollama installed successfully"
        return 0
    else
        print_error "Failed to install Ollama"
        return 1
    fi
}

# Function to install Ollama
install_ollama() {
    print_status "Installing Ollama..."
    
    # Detect system information
    local system_info=$(detect_system)
    local os_name=$(echo "$system_info" | cut -d'|' -f1)
    local arch=$(echo "$system_info" | cut -d'|' -f2)
    local package_manager=$(echo "$system_info" | cut -d'|' -f3)
    local install_method=$(echo "$system_info" | cut -d'|' -f4)
    
    print_status "Detected: $os_name ($arch) with $package_manager"
    
    case "$os_name" in
        "macOS")
            # macOS installation (existing logic)
            print_status "Detected macOS ($arch)"
            
            # Try to configure Homebrew PATH if it's installed but not in PATH
            configure_homebrew_path
            
            # Check if Homebrew is available
            if command_exists brew; then
                print_status "Installing Ollama via Homebrew..."
                
                # Check if Ollama is already installed via Homebrew
                if brew list ollama >/dev/null 2>&1; then
                    print_success "Ollama is already installed via Homebrew"
                else
                    if brew install ollama; then
                        print_success "Ollama installed successfully via Homebrew"
                    else
                        print_warning "Homebrew installation failed, trying manual download..."
                    fi
                fi
                
                # Verify and start Ollama service
                if verify_and_start_ollama; then
                    return 0
                else
                    print_warning "Ollama installed but service verification failed"
                    return 1
                fi
            else
                # Homebrew not available, ask user if they want to install it
                print_warning "Homebrew not found"
                print_status "Homebrew makes package installation much easier on macOS"
                
                echo ""
                read -p "Would you like to install Homebrew first? (y/n): " -n 1 -r
                echo ""
                
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    if install_homebrew; then
                        # Try installing Ollama with Homebrew again
                        print_status "Installing Ollama via Homebrew..."
                        
                        # Check if Ollama is already installed via Homebrew
                        if brew list ollama >/dev/null 2>&1; then
                            print_success "Ollama is already installed via Homebrew"
                        else
                            if brew install ollama; then
                                print_success "Ollama installed successfully via Homebrew"
                            else
                                print_warning "Homebrew Ollama installation failed, trying manual download..."
                            fi
                        fi
                        
                        # Verify and start Ollama service
                        if verify_and_start_ollama; then
                            return 0
                        else
                            print_warning "Ollama installed but service verification failed"
                            return 1
                        fi
                    else
                        print_warning "Homebrew installation failed, trying manual download..."
                    fi
                else
                    print_status "Skipping Homebrew installation, trying manual download..."
                fi
            fi
            
            # Manual download for macOS
            print_status "Downloading Ollama for macOS..."
            print_status "Please visit https://ollama.ai/download to download the macOS installer"
            print_status "Or run: brew install ollama (if you have Homebrew)"
            
            # Try to open the download page
            if command_exists open; then
                print_status "Opening Ollama download page..."
                open "https://ollama.ai/download"
            fi
            
            print_error "Automatic installation not available for macOS"
            print_status "Please download and install Ollama manually from https://ollama.ai/download"
            return 1
            ;;
            
        "Linux")
            # Linux installation
            print_status "Detected Linux ($arch) with $package_manager"
            
            if install_ollama_linux "$install_method"; then
                # Verify and start Ollama service
                if verify_and_start_ollama; then
                    return 0
                else
                    print_warning "Ollama installed but service verification failed"
                    return 1
                fi
            else
                print_error "Failed to install Ollama on Linux"
                return 1
            fi
            ;;
            
        "Windows")
            # Windows installation
            print_status "Detected Windows ($arch)"
            
            if install_ollama_windows; then
                print_success "Ollama installed successfully on Windows"
                print_status "Please restart your terminal or command prompt"
                print_status "Then run this script again"
                return 0
            else
                print_error "Failed to install Ollama on Windows"
                return 1
            fi
            ;;
            
        *)
            print_error "Unsupported operating system: $os_name"
            print_status "Please install Ollama manually from https://ollama.ai"
            return 1
            ;;
    esac
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        print_status "Please install Python 3 from https://python.org"
        exit 1
    fi
    
    local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python version: $python_version"
    
    # Configure Homebrew PATH if needed (for macOS)
    if [[ "$(uname -s)" == "Darwin" ]]; then
        configure_homebrew_path || true  # Don't exit on error
        
        # Check if ollama is still not available after PATH config
        if ! command_exists ollama; then
            print_status "Configuring shell environment permanently..."
            if [[ -f "./scripts/setup/configure_shell.sh" ]]; then
                bash ./scripts/setup/configure_shell.sh >/dev/null 2>&1 || true
                print_success "Shell environment configured for future sessions"
                print_status "Run 'source ~/.zshrc' or open a new terminal to use 'ollama' command"
            fi
        fi
    fi
    
    # Check Ollama installation and service status
    if ! command_exists ollama; then
        print_warning "Ollama is not installed"
        print_status "Ollama is required for AI-powered code analysis"
        
        # Ask user if they want to install Ollama
        echo ""
        read -p "Would you like to install Ollama automatically? (y/n): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if install_ollama; then
                print_success "Ollama installation and configuration completed"
                print_status "Shell environment has been automatically configured"
                print_status "Continuing with application startup..."
                # Don't exit, continue with the script
            else
                print_error "Automatic installation failed"
                print_status "For macOS: Please download from https://ollama.ai/download or install Homebrew first then run 'brew install ollama'"
                print_status "For Linux: Please run 'curl -fsSL https://ollama.com/install.sh | sh'"
                print_status "For Windows: Please download from https://ollama.ai/download or install via Chocolatey/Winget"
                print_status "After installation, run this script again"
                exit 1
            fi
        else
            print_error "Ollama installation declined"
            print_status "For macOS: Please download from https://ollama.ai/download or install Homebrew first then run 'brew install ollama'"
            print_status "For Linux: Please run 'curl -fsSL https://ollama.com/install.sh | sh'"
            print_status "For Windows: Please download from https://ollama.ai/download or install via Chocolatey/Winget"
            print_status "After installation, run this script again"
            exit 1
        fi
    else
        # Ollama is installed, check if service is running
        print_status "Ollama is installed, checking service status..."
        
        # Check if Ollama service is running
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            print_success "Ollama service is running"
            local ollama_version=$(ollama --version 2>&1 | grep -v "Warning" | head -n1)
            print_success "Ollama version: $ollama_version"
        else
            print_status "Ollama service is not running (this is normal)"
            print_status "The script will start the Ollama service automatically"
        fi
    fi
    
    # Check if we're in the right directory
    if [ ! -f "sec360.py" ]; then
        print_error "sec360.py not found. Please run this script from the project root directory"
        exit 1
    fi
    
    print_success "All requirements satisfied"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs
    mkdir -p core/logs
    mkdir -p config
    
    print_success "Directories created"
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Install required packages for system Python
    python3 -m pip install requests --quiet --no-warn-script-location
    python3 -m pip install "psutil>=5.9.0" --quiet --no-warn-script-location
    python3 -m pip install tkinter --quiet --no-warn-script-location 2>/dev/null || print_status "tkinter is built into Python (no installation needed)"
    
    print_success "Python dependencies installed"
}

# Function to start Ollama service
start_ollama() {
    print_status "Starting Ollama service..."
    
    # Check if Ollama is already running
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_success "Ollama service is already running"
        return 0
    fi
    
    # Start Ollama in background
    nohup ollama serve > logs/ollama.log 2>&1 &
    local ollama_pid=$!
    
    # Wait for Ollama to start
    print_status "Waiting for Ollama service to start..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            print_success "Ollama service started successfully (PID: $ollama_pid)"
            echo $ollama_pid > logs/ollama.pid
            return 0
        fi
        
        attempt=$((attempt + 1))
        sleep 1
        print_status "Attempt $attempt/$max_attempts - Waiting for Ollama..."
    done
    
    print_error "Failed to start Ollama service"
    return 1
}

# Function to check and install required models
check_and_install_models() {
    print_status "Checking for required models..."
    
    # Get list of available models
    local available_models=$(ollama list 2>/dev/null | awk 'NR>1 {print $1}' || true)
    
    if [ -z "$available_models" ]; then
        print_warning "No models found. Installing recommended model..."
        install_recommended_model
        return
    fi
    
    # Mac Silicon optimized models for practice
    if [[ $(uname -m) == "arm64" ]]; then
        # Mac Silicon optimized models (smaller, faster, more efficient)
        local recommended_model="llama3.2:3b"
        print_status "Setting up Mac Silicon optimized model..."
    else
        # Fallback for Intel Macs
        local recommended_model="llama3.2:3b"  # Still use 3b for better performance
        print_status "Setting up standard model..."
    fi
    
    # Check if recommended model is available
    if echo "$available_models" | grep -q "^$recommended_model$"; then
        print_success "Model $recommended_model is available"
    else
        print_warning "Recommended model $recommended_model not found"
        install_recommended_model "$recommended_model"
    fi
    
    # Show all available models
    print_status "Available models:"
    echo "$available_models" | while read -r model; do
        if [ -n "$model" ]; then
            echo "  - $model"
        fi
    done
}

# Function to install recommended model
install_recommended_model() {
    local model=${1:-"llama3.2:3b"}
    
    print_status "Installing recommended model: $model"
    print_status "This may take several minutes depending on your internet connection..."
    
    # Ask user if they want to install the model
    echo ""
    read -p "Would you like to install the recommended model ($model) now? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Pulling model $model..."
        if ollama pull "$model" 2>&1 | tee -a logs/ollama.log; then
            print_success "Successfully installed $model"
        else
            print_warning "Failed to install $model"
            print_status "You can install models manually later using: ollama pull $model"
        fi
    else
        print_warning "Model installation skipped"
        print_status "You can install models manually later using: ollama pull $model"
        print_status "Or run: ollama pull llama3.2:3b"
    fi
}

# Function to pull recommended models (legacy - keeping for compatibility)
pull_models() {
    check_and_install_models
}

# Function to start the main application
start_application() {
    print_status "Starting Sec360 Application..."
    
    # Start the application in background
    nohup python3 sec360.py > logs/application.log 2>&1 &
    local app_pid=$!
    
    # Wait a moment for the application to start
    sleep 3
    
    # Check if the application is running
    if kill -0 $app_pid 2>/dev/null; then
        print_success "Application started successfully (PID: $app_pid)"
        echo $app_pid > logs/application.pid
        return 0
    else
        print_error "Failed to start application"
        return 1
    fi
}

# Function to show status
show_status() {
    print_status "Service Status:"
    
    # Check Ollama
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_success "Ollama service: Running"
    else
        print_error "Ollama service: Not running"
    fi
    
    # Check Application
    if [ -f "logs/application.pid" ]; then
        local app_pid=$(cat logs/application.pid)
        if kill -0 $app_pid 2>/dev/null; then
            print_success "Application: Running (PID: $app_pid)"
        else
            print_error "Application: Not running"
        fi
    else
        print_error "Application: Not running"
    fi
    
    # Show available models
    print_status "Available models:"
    local models=$(ollama list 2>/dev/null | awk 'NR>1 {print $1}' || true)
    if [ -n "$models" ]; then
        echo "$models" | while read -r model; do
            if [ -n "$model" ]; then
                echo "  - $model"
            fi
        done
    else
        print_warning "No models found"
        print_status "Run 'ollama pull llama3.2:3b' to install a model"
    fi
}

# Main execution
main() {
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                           Sec360 by Abhay                                    ║"
    echo "║              Advanced Code Security Analysis Platform - Start Script         ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo " ____            _____  __    ___    _                _    _     _                  "
    echo "/ ___|  ___  ___|___ / / /_  / _ \  | |__  _   _     / \  | |__ | |__   __ _ _   _  "
    echo "\___ \ / _ \/ __| |_ \| '_ \| | | | | '_ \| | | |   / _ \ | '_ \| '_ \ / _\` | | | | "
    echo " ___) |  __/ (__ ___) | (_) | |_| | | |_) | |_| |  / ___ \| |_) | | | | (_| | |_| | "
    echo "|____/ \___|\___|____/ \___/ \___/  |_.__/ \__, | /_/   \_\_.__/|_| |_|\__,_|\__, | "
    echo "                                           |___/                             |___/   "
    echo ""
    echo ""
    # Change to project root directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
    cd "$PROJECT_ROOT"
    
    echo "📁 Working directory: $(pwd)"
    
    # Clean startup - kill existing services
    print_status "Performing clean startup..."
    
    # Kill processes on common ports
    kill_port 11434 "Ollama"
    kill_port 8000 "Application"
    kill_port 5000 "Flask"
    kill_port 3000 "Development"
    
    # Kill existing processes
    kill_process "ollama"
    kill_process "sec360\.py"
    kill_process "scoreboard_launcher\.py"
    kill_process "llm-safety-trainer"
    
    # Stop Docker containers
    stop_containers
    
    # Clean up Python processes
    cleanup_python
    
    # Wait a moment for cleanup
    sleep 2
    
    print_success "Clean startup completed"
    
    # Create directories first (needed for Ollama logs)
    create_directories
    
    # Check requirements
    check_requirements
    
    # Install dependencies
    install_dependencies
    
    # Verify and start Ollama service
    if ! verify_and_start_ollama; then
        print_error "Failed to start Ollama service"
        exit 1
    fi
    
    # Check and install models
    check_and_install_models
    
    # Start application
    if ! start_application; then
        print_error "Failed to start application"
        exit 1
    fi
    
    # Show status
    echo ""
    show_status
    
    echo ""
    print_success "Sec360 by Abhay started successfully!"
    print_status "Application logs: logs/application.log"
    print_status "Ollama logs: logs/ollama.log"
    print_status "To stop the application, run: ./scripts/management/stop.sh"
    print_status "To view logs, run: tail -f logs/application.log"
}

# Run main function
main "$@"