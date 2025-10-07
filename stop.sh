#!/bin/bash

# Sec360 by Abhay - Advanced Code Security Analysis Platform - Stop Script
# This script stops all services and cleans up processes

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
            kill -TERM $pid 2>/dev/null || true
        done
        sleep 2
        
        # Force kill if still running
        local remaining_pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$remaining_pids" ]; then
            print_warning "Force killing remaining processes on port $port: $remaining_pids"
            for pid in $remaining_pids; do
                kill -9 $pid 2>/dev/null || true
            done
        fi
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
        
        # Clean up unused images
        print_status "Cleaning up unused Docker images..."
        docker image prune -f 2>/dev/null || true
        print_success "Cleaned up unused Docker images"
    else
        print_status "Docker not found, skipping container cleanup"
    fi
}

# Function to stop application using PID file
stop_application() {
    print_status "Stopping application..."
    
    if [ -f "logs/application.pid" ]; then
        local app_pid=$(cat logs/application.pid)
        if kill -0 $app_pid 2>/dev/null; then
            print_status "Stopping application (PID: $app_pid)"
            kill -TERM $app_pid 2>/dev/null || true
            sleep 3
            
            # Check if still running
            if kill -0 $app_pid 2>/dev/null; then
                print_warning "Application still running, force killing..."
                kill -9 $app_pid 2>/dev/null || true
            fi
            print_success "Application stopped"
        else
            print_warning "Application PID file exists but process not running"
        fi
        rm -f logs/application.pid
    else
        print_status "No application PID file found"
    fi
}

# Function to stop Ollama using PID file
stop_ollama() {
    print_status "Stopping Ollama service..."
    
    if [ -f "logs/ollama.pid" ]; then
        local ollama_pid=$(cat logs/ollama.pid)
        if kill -0 $ollama_pid 2>/dev/null; then
            print_status "Stopping Ollama service (PID: $ollama_pid)"
            kill -TERM $ollama_pid 2>/dev/null || true
            sleep 3
            
            # Check if still running
            if kill -0 $ollama_pid 2>/dev/null; then
                print_warning "Ollama still running, force killing..."
                kill -9 $ollama_pid 2>/dev/null || true
            fi
            print_success "Ollama service stopped"
        else
            print_warning "Ollama PID file exists but process not running"
        fi
        rm -f logs/ollama.pid
    else
        print_status "No Ollama PID file found"
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

# Function to clean up log files
cleanup_logs() {
    print_status "Cleaning up log files..."
    
    if [ -d "logs" ]; then
        # Keep recent logs but clean up old ones
        find logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
        find logs -name "*.pid" -delete 2>/dev/null || true
        print_success "Cleaned up old log files"
    else
        print_status "No logs directory found"
    fi
}

# Function to show status
show_status() {
    print_status "Service Status:"
    
    # Check Ollama
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        print_warning "Ollama service: Still running"
    else
        print_success "Ollama service: Stopped"
    fi
    
    # Check Application
    if [ -f "logs/application.pid" ]; then
        local app_pid=$(cat logs/application.pid)
        if kill -0 $app_pid 2>/dev/null; then
            print_warning "Application: Still running (PID: $app_pid)"
        else
            print_success "Application: Stopped"
        fi
    else
        print_success "Application: Stopped"
    fi
    
    # Check for remaining processes
    local remaining_processes=$(pgrep -f "sec360\.py\|scoreboard_launcher\.py\|llm-safety-trainer" 2>/dev/null || true)
    if [ -n "$remaining_processes" ]; then
        print_warning "Remaining processes: $remaining_processes"
    else
        print_success "All processes stopped"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -f, --force    Force stop all processes without confirmation"
    echo "  -c, --clean    Clean up log files and temporary data"
    echo "  -s, --status   Show current status and exit"
    echo ""
    echo "Examples:"
    echo "  $0              # Stop services with confirmation"
    echo "  $0 --force      # Force stop without confirmation"
    echo "  $0 --clean      # Stop and clean up logs"
    echo "  $0 --status     # Show status only"
}

# Function to confirm action
confirm_action() {
    if [ "$FORCE" = "true" ]; then
        return 0
    fi
    
    echo -n "Are you sure you want to stop all services? (y/N): "
    read -r response
    case "$response" in
        [yY][eE][sS]|[yY])
            return 0
            ;;
        *)
            print_status "Operation cancelled"
            exit 0
            ;;
    esac
}

# Parse command line arguments
FORCE=false
CLEAN=false
STATUS_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -s|--status)
            STATUS_ONLY=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    echo "🛑 Sec360 by Abhay - Advanced Code Security Analysis Platform - Stop Script"
    echo "=========================================================================="
    
    # Change to project root directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
    cd "$PROJECT_ROOT"
    
    echo "📁 Working directory: $(pwd)"
    
    # Show status if requested
    if [ "$STATUS_ONLY" = "true" ]; then
        show_status
        exit 0
    fi
    
    # Confirm action
    confirm_action
    
    print_status "Stopping all services..."
    
    # Stop application using PID file
    stop_application
    
    # Stop Ollama using PID file
    stop_ollama
    
    # Kill processes on common ports
    kill_port 11434 "Ollama"
    kill_port 8000 "Application"
    kill_port 5000 "Flask"
    kill_port 3000 "Development"
    
    # Kill existing processes
    kill_process "ollama"
    kill_process "sec360\.py"
    kill_process "scoreboard_launcher\.py"
    
    # Stop Docker containers
    stop_containers
    
    # Clean up Python processes
    cleanup_python
    
    # Clean up logs if requested
    if [ "$CLEAN" = "true" ]; then
        cleanup_logs
    fi
    
    # Wait a moment for cleanup
    sleep 2
    
    # Show final status
    echo ""
    show_status
    
    echo ""
    print_success "All services stopped successfully!"
    
    if [ "$CLEAN" = "true" ]; then
        print_success "Log files cleaned up"
    fi
    
    print_status "To start the application again, run: ./scripts/management/start.sh"
}

# Run main function
main "$@"