#!/bin/bash

# Sec360 Shell Configuration Script
# This script configures your shell environment to make ollama and other tools available globally

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

# Function to configure shell environment
configure_shell_environment() {
    print_status "Configuring shell environment for Sec360..."
    
    # Detect shell type
    local shell_name=$(basename "$SHELL")
    local shell_config_file=""
    
    case "$shell_name" in
        "zsh")
            shell_config_file="$HOME/.zshrc"
            print_status "Detected zsh shell, using .zshrc"
            ;;
        "bash")
            shell_config_file="$HOME/.bashrc"
            print_status "Detected bash shell, using .bashrc"
            ;;
        *)
            shell_config_file="$HOME/.profile"
            print_status "Using .profile as fallback for $shell_name"
            ;;
    esac
    
    # Determine Homebrew path based on architecture
    local homebrew_path=""
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        homebrew_path="/opt/homebrew/bin"
        print_status "Using Apple Silicon Homebrew path"
    elif [[ -f "/usr/local/bin/brew" ]]; then
        homebrew_path="/usr/local/bin"
        print_status "Using Intel Mac Homebrew path"
    else
        print_warning "Homebrew not found, skipping PATH configuration"
        return 1
    fi
    
    # Check if Homebrew is already in the config file
    if [[ -f "$shell_config_file" ]] && grep -q "homebrew" "$shell_config_file" 2>/dev/null; then
        print_success "Homebrew already configured in $shell_config_file"
        return 0
    fi
    
    # Create backup of existing config file
    if [[ -f "$shell_config_file" ]]; then
        cp "$shell_config_file" "${shell_config_file}.backup.$(date +%Y%m%d_%H%M%S)"
        print_status "Created backup: ${shell_config_file}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Add Homebrew to PATH
    print_status "Adding Homebrew to PATH in $shell_config_file..."
    
    cat >> "$shell_config_file" << EOF

# Sec360 - Homebrew PATH Configuration
# Added by Sec360 setup script on $(date)
export PATH="$homebrew_path:\$PATH"
export HOMEBREW_NO_AUTO_UPDATE=1
export HOMEBREW_NO_INSTALL_CLEANUP=1

EOF
    
    print_success "Homebrew PATH added to $shell_config_file"
    
    # Source the config file for current session
    print_status "Sourcing $shell_config_file for current session..."
    source "$shell_config_file" 2>/dev/null || true
    
    print_success "Shell environment configured successfully!"
    print_status "You can now use 'ollama' command in new terminal sessions"
    print_warning "For current session, run: source $shell_config_file"
    
    return 0
}

# Function to test ollama availability
test_ollama() {
    print_status "Testing ollama command availability..."
    
    if command_exists ollama; then
        print_success "✅ ollama command is available"
        local ollama_version=$(ollama --version 2>&1 | grep -v "Warning" | head -n1)
        print_success "Ollama version: $ollama_version"
        return 0
    else
        print_warning "❌ ollama command not found in PATH"
        return 1
    fi
}

# Main function
main() {
    echo "🔧 Sec360 Shell Configuration Script"
    echo "===================================="
    echo ""
    
    # Check if we're on macOS
    if [[ "$(uname -s)" != "Darwin" ]]; then
        print_error "This script is designed for macOS only"
        print_status "For Linux/Windows, please configure your shell manually"
        exit 1
    fi
    
    # Configure shell environment
    if configure_shell_environment; then
        print_success "Shell configuration completed!"
        
        # Test ollama availability
        if test_ollama; then
            print_success "🎉 ollama command is now available!"
        else
            print_warning "ollama command not yet available in current session"
            print_status "Please run: source ~/.zshrc (or ~/.bashrc)"
            print_status "Or open a new terminal window"
        fi
        
        echo ""
        print_status "Next steps:"
        print_status "1. Open a new terminal window, OR"
        print_status "2. Run: source ~/.zshrc (or ~/.bashrc depending on your shell)"
        print_status "3. Test: ollama --version"
        
    else
        print_error "Shell configuration failed"
        exit 1
    fi
}

# Run main function
main "$@"
