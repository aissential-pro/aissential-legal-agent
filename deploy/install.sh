#!/bin/bash
#
# AIssential Legal Agent - Installation Script for Ubuntu VPS
# This script installs and configures the AIssential Legal Agent
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/aissential-legal-agent"
GITHUB_REPO="https://github.com/your-username/aissential-legal-agent.git"  # Update this
REQUIRED_PYTHON_VERSION="3.10"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  AIssential Legal Agent Installer${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to compare version numbers
version_ge() {
    [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" = "$2" ]
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Please run this script as root (sudo)${NC}"
    exit 1
fi

# Step 1: Check Python version
echo -e "${YELLOW}[1/7] Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    echo "       Found Python $PYTHON_VERSION"

    if version_ge "$PYTHON_VERSION" "$REQUIRED_PYTHON_VERSION"; then
        echo -e "       ${GREEN}Python version OK${NC}"
    else
        echo -e "${RED}Error: Python $REQUIRED_PYTHON_VERSION or higher is required (found $PYTHON_VERSION)${NC}"
        echo "       Please install Python $REQUIRED_PYTHON_VERSION+ and try again"
        exit 1
    fi
else
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "       Please install Python $REQUIRED_PYTHON_VERSION+ and try again"
    echo "       Ubuntu: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# Check for python3-venv
echo -e "${YELLOW}[2/7] Checking for python3-venv...${NC}"
if ! python3 -m venv --help &> /dev/null; then
    echo "       Installing python3-venv..."
    apt-get update
    apt-get install -y python3-venv
fi
echo -e "       ${GREEN}python3-venv OK${NC}"

# Step 3: Create installation directory
echo -e "${YELLOW}[3/7] Creating installation directory...${NC}"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "       ${YELLOW}Warning: $INSTALL_DIR already exists${NC}"
    read -p "       Do you want to remove it and continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
    else
        echo "       Installation cancelled"
        exit 1
    fi
fi
mkdir -p "$INSTALL_DIR"
echo -e "       ${GREEN}Created $INSTALL_DIR${NC}"

# Step 4: Clone or copy files
echo -e "${YELLOW}[4/7] Installing application files...${NC}"

# Check if we're running from the project directory (local install)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_DIR/requirements.txt" ] && [ -d "$PROJECT_DIR/app" ]; then
    echo "       Copying files from local directory..."
    cp -r "$PROJECT_DIR/app" "$INSTALL_DIR/"
    cp "$PROJECT_DIR/requirements.txt" "$INSTALL_DIR/"

    # Copy .env.example if it exists
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp "$PROJECT_DIR/.env.example" "$INSTALL_DIR/"
    fi

    # Copy CONTEXT.md if it exists
    if [ -f "$PROJECT_DIR/CONTEXT.md" ]; then
        cp "$PROJECT_DIR/CONTEXT.md" "$INSTALL_DIR/"
    fi

    echo -e "       ${GREEN}Files copied from local directory${NC}"
else
    echo "       Cloning from GitHub..."
    if command -v git &> /dev/null; then
        git clone "$GITHUB_REPO" "$INSTALL_DIR"
        echo -e "       ${GREEN}Repository cloned${NC}"
    else
        echo -e "${RED}Error: git is not installed and local files not found${NC}"
        echo "       Please install git: sudo apt install git"
        exit 1
    fi
fi

# Step 5: Create virtual environment
echo -e "${YELLOW}[5/7] Creating Python virtual environment...${NC}"
python3 -m venv "$INSTALL_DIR/venv"
echo -e "       ${GREEN}Virtual environment created${NC}"

# Step 6: Install requirements
echo -e "${YELLOW}[6/7] Installing Python dependencies...${NC}"
source "$INSTALL_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$INSTALL_DIR/requirements.txt"
deactivate
echo -e "       ${GREEN}Dependencies installed${NC}"

# Step 7: Create logs directory and set permissions
echo -e "${YELLOW}[7/7] Setting up logs and permissions...${NC}"
mkdir -p "$INSTALL_DIR/logs"

# Set ownership (optional: create dedicated user)
# useradd -r -s /bin/false aissential 2>/dev/null || true
# chown -R aissential:aissential "$INSTALL_DIR"

# Set permissions
chmod -R 755 "$INSTALL_DIR"
chmod -R 775 "$INSTALL_DIR/logs"

echo -e "       ${GREEN}Logs directory created and permissions set${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. Configure environment variables:"
echo "   sudo nano $INSTALL_DIR/.env"
echo ""
echo "   Required variables:"
echo "   - OPENAI_API_KEY=your_openai_api_key"
echo "   - GMAIL_ADDRESS=your_gmail@gmail.com"
echo "   - GMAIL_APP_PASSWORD=your_app_password"
echo "   - TO_EMAIL=destination@email.com"
echo ""
echo "2. Test the agent manually:"
echo "   cd $INSTALL_DIR"
echo "   source venv/bin/activate"
echo "   python -m app.main"
echo ""
echo "3. Set up scheduled execution (choose one):"
echo "   - Cron: sudo ./deploy/setup-cron.sh"
echo "   - Systemd: sudo cp deploy/*.service deploy/*.timer /etc/systemd/system/"
echo "             sudo systemctl enable --now aissential-agent.timer"
echo ""
echo -e "${GREEN}Installation directory: $INSTALL_DIR${NC}"
echo ""
