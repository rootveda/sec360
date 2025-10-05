#!/bin/bash

# Sec360 Uninstall Script
# This script removes all dependencies installed by the start.sh script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to stop all Sec360 services
stop_services() {
    print_status "Stopping all Sec360 services..."
    
    # Stop Ollama service
    if pgrep -f "ollama serve" >/dev/null; then
        print_status "Stopping Ollama service..."
        pkill -f "ollama serve" || true
        sleep 2
        print_success "Ollama service stopped"
    else
        print_status "No Ollama service running"
    fi
    
    # Stop Sec360 application
    if pgrep -f "sec360.py" >/dev/null; then
        print_status "Stopping Sec360 application..."
        pkill -f "sec360.py" || true
        sleep 2
        print_success "Sec360 application stopped"
    else
        print_status "No Sec360 application running"
    fi
    
    # Stop other related processes
    if pgrep -f "scoreboard_launcher.py" >/dev/null; then
        print_status "Stopping scoreboard launcher..."
        pkill -f "scoreboard_launcher.py" || true
    fi
    
    if pgrep -f "llm-safety-trainer" >/dev/null; then
        print_status "Stopping LLM safety trainer..."
        pkill -f "llm-safety-trainer" || true
    fi
    
    print_success "All services stopped"
}

# Function to uninstall Python dependencies
uninstall_python_deps() {
    print_status "Uninstalling Python dependencies..."
    
    # List of packages to uninstall
    local packages=("requests" "psutil")
    
    for package in "${packages[@]}"; do
        if python3 -m pip show "$package" >/dev/null 2>&1; then
            print_status "Uninstalling $package..."
            python3 -m pip uninstall "$package" -y --quiet
            print_success "$package uninstalled"
        else
            print_status "$package not installed via pip"
        fi
    done
    
    # Note: tkinter is built into Python, so we don't uninstall it
    print_status "tkinter is built into Python (not uninstalled)"
    
    print_success "Python dependencies uninstalled"
}

# Function to uninstall Ollama
uninstall_ollama() {
    print_status "Checking Ollama installation..."
    
    if command_exists ollama; then
        print_status "Ollama is installed, checking installation method..."
        
        # Check if installed via Homebrew
        if command_exists brew && brew list ollama >/dev/null 2>&1; then
            print_status "Ollama installed via Homebrew, uninstalling..."
            if brew uninstall ollama; then
                print_success "Ollama uninstalled via Homebrew"
            else
                print_warning "Failed to uninstall Ollama via Homebrew"
            fi
        else
            print_warning "Ollama not installed via Homebrew"
            print_status "Ollama may have been installed manually"
            print_status "Please uninstall manually from: https://ollama.ai/"
        fi
        
        # Remove Ollama models directory
        if [[ -d "$HOME/.ollama" ]]; then
            print_status "Removing Ollama models directory..."
            rm -rf "$HOME/.ollama"
            print_success "Ollama models directory removed"
        fi
        
    else
        print_status "Ollama not found in PATH"
    fi
}

# Function to remove shell configuration
remove_shell_config() {
    print_status "Checking shell configuration..."
    
    # Detect shell type
    local shell_name=$(basename "$SHELL")
    local shell_config_file=""
    
    case "$shell_name" in
        "zsh")
            shell_config_file="$HOME/.zshrc"
            ;;
        "bash")
            shell_config_file="$HOME/.bashrc"
            ;;
        *)
            shell_config_file="$HOME/.profile"
            ;;
    esac
    
    if [[ -f "$shell_config_file" ]]; then
        # Check if Sec360 configuration exists
        if grep -q "Sec360" "$shell_config_file" 2>/dev/null; then
            print_status "Found Sec360 configuration in $shell_config_file"
            
            # Create backup before removing
            cp "$shell_config_file" "${shell_config_file}.backup.before_uninstall.$(date +%Y%m%d_%H%M%S)"
            print_status "Created backup: ${shell_config_file}.backup.before_uninstall.$(date +%Y%m%d_%H%M%S)"
            
            # Remove Sec360 configuration lines
            sed -i.tmp '/# Sec360 - Homebrew PATH Configuration/,/^$/d' "$shell_config_file"
            rm -f "${shell_config_file}.tmp"
            
            print_success "Sec360 configuration removed from $shell_config_file"
        else
            print_status "No Sec360 configuration found in $shell_config_file"
        fi
    else
        print_status "Shell config file $shell_config_file not found"
    fi
}

# Function to clean up logs and temporary files
cleanup_files() {
    print_status "Cleaning up Sec360 files..."
    
    # Remove logs directory
    if [[ -d "logs" ]]; then
        print_status "Removing logs directory..."
        rm -rf logs
        print_success "Logs directory removed"
    fi
    
    # Remove config directory
    if [[ -d "config" ]]; then
        print_status "Removing config directory..."
        rm -rf config
        print_success "Config directory removed"
    fi
    
    # Remove any temporary files
    if [[ -d "/tmp/sec360" ]]; then
        print_status "Removing temporary files..."
        rm -rf /tmp/sec360
        print_success "Temporary files removed"
    fi
    
    print_success "File cleanup completed"
}

# Function to show what will be uninstalled
show_uninstall_summary() {
    echo "🧹 Sec360 Uninstall Summary"
    echo "=========================="
    echo ""
    
    print_status "The following will be uninstalled:"
    echo "  📦 Python packages: requests, psutil"
    echo "  🤖 Ollama (if installed via Homebrew)"
    echo "  📁 Ollama models directory (~/.ollama)"
    echo "  ⚙️  Shell configuration (Homebrew PATH)"
    echo "  📝 Logs and config directories"
    echo "  🗑️  Temporary files"
    echo ""
    
    print_warning "This will completely remove Sec360 dependencies"
    print_warning "You can reinstall them by running ./scripts/management/start.sh"
    echo ""
}

# Main function
main() {
    echo "🧹 Sec360 by Abhay - Uninstall Script"
    echo "======================================"
    echo ""
    
    # Show what will be uninstalled
    show_uninstall_summary
    
    # Ask for confirmation
    read -p "Are you sure you want to uninstall all Sec360 dependencies? (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Uninstall cancelled"
        exit 0
    fi
    
    echo ""
    print_status "Starting uninstall process..."
    echo ""
    
    # Stop all services first
    stop_services
    echo ""
    
    # Uninstall Python dependencies
    uninstall_python_deps
    echo ""
    
    # Uninstall Ollama
    uninstall_ollama
    echo ""
    
    # Remove shell configuration
    remove_shell_config
    echo ""
    
    # Clean up files
    cleanup_files
    echo ""
    
    print_success "🎉 Sec360 uninstall completed!"
    echo ""
    print_status "Summary:"
    print_status "  ✅ All services stopped"
    print_status "  ✅ Python dependencies removed"
    print_status "  ✅ Ollama uninstalled (if via Homebrew)"
    print_status "  ✅ Shell configuration cleaned"
    print_status "  ✅ Files cleaned up"
    echo ""
    print_status "To reinstall everything, run: ./scripts/management/start.sh"
}

# Run main function
main "$@"
