#!/bin/bash

# Browser Fingerprinting Platform - Development Setup Script
# This script sets up the development environment for the BFP project

set -e

echo "🚀 Setting up Browser Fingerprinting Platform Development Environment"
echo "================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Python 3.9+ is installed
check_python() {
    print_info "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 9) else 1)'; then
            print_status "Python $PYTHON_VERSION found ✓"
        else
            print_error "Python 3.9+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.9+"
        exit 1
    fi
}

# Check if MongoDB is available
check_mongodb() {
    print_info "Checking MongoDB connection..."
    if command -v mongosh &> /dev/null || command -v mongo &> /dev/null; then
        print_status "MongoDB client found ✓"
    else
        print_warning "MongoDB client not found. Install MongoDB Community Edition"
        echo "Visit: https://www.mongodb.com/try/download/community"
    fi
}

# Check if Redis is available
check_redis() {
    print_info "Checking Redis connection..."
    if command -v redis-cli &> /dev/null; then
        print_status "Redis client found ✓"
    else
        print_warning "Redis client not found. Install Redis"
        echo "Visit: https://redis.io/download"
    fi
}

# Create virtual environment
setup_venv() {
    print_info "Setting up Python virtual environment..."
    if [ ! -d "bfp" ]; then
        python3 -m venv bfp
        print_status "Virtual environment created ✓"
    else
        print_status "Virtual environment already exists ✓"
    fi
}

# Activate virtual environment and install dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    # Activate virtual environment
    source bfp/bin/activate 2>/dev/null || source bfp/Scripts/activate 2>/dev/null || {
        print_error "Failed to activate virtual environment"
        exit 1
    }
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install production dependencies
    pip install -r requirements.txt
    
    # Install development dependencies if available
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
        print_status "Development dependencies installed ✓"
    fi
    
    print_status "Dependencies installed ✓"
}

# Setup environment file
setup_env() {
    print_info "Setting up environment configuration..."
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_status "Environment file created from template ✓"
        print_warning "Please edit .env file with your configuration"
    else
        print_status "Environment file already exists ✓"
    fi
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    mkdir -p logs
    mkdir -p uploads
    mkdir -p backups
    print_status "Directories created ✓"
}

# Setup pre-commit hooks (if available)
setup_precommit() {
    if command -v pre-commit &> /dev/null; then
        print_info "Setting up pre-commit hooks..."
        pre-commit install
        print_status "Pre-commit hooks installed ✓"
    fi
}

# Test the installation
test_installation() {
    print_info "Testing installation..."
    
    # Activate virtual environment
    source bfp/bin/activate 2>/dev/null || source bfp/Scripts/activate 2>/dev/null
    
    # Test imports
    python3 -c "
import fastapi
import motor
import redis
import pydantic
print('✓ All required packages imported successfully')
    " || {
        print_error "Package import test failed"
        exit 1
    }
    
    print_status "Installation test passed ✓"
}

# Main setup process
main() {
    echo
    print_info "Starting development environment setup..."
    echo
    
    check_python
    check_mongodb
    check_redis
    setup_venv
    install_dependencies
    setup_env
    create_directories
    setup_precommit
    test_installation
    
    echo
    echo "================================================================="
    echo -e "${GREEN}🎉 Development environment setup complete!${NC}"
    echo "================================================================="
    echo
    echo "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Start MongoDB and Redis services"
    echo "3. Activate virtual environment:"
    echo "   source bfp/bin/activate  # Linux/Mac"
    echo "   bfp\\Scripts\\activate     # Windows"
    echo "4. Run the application:"
    echo "   uvicorn main:app --reload"
    echo "5. Visit http://localhost:8000 in your browser"
    echo
    echo "For more information, see README.md"
    echo
}

# Run main function
main "$@"
