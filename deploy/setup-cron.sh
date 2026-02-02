#!/bin/bash
#
# AIssential Legal Agent - Cron Setup Script
# Sets up a cron job to run the agent every 30 minutes
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/aissential-legal-agent"
CRON_SCHEDULE="*/30 * * * *"  # Every 30 minutes
LOG_FILE="$INSTALL_DIR/logs/cron.log"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  AIssential Legal Agent - Cron Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: Please run this script as root (sudo)${NC}"
    exit 1
fi

# Check if installation exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}Error: Installation not found at $INSTALL_DIR${NC}"
    echo "       Please run install.sh first"
    exit 1
fi

if [ ! -f "$INSTALL_DIR/venv/bin/python" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "       Please run install.sh first"
    exit 1
fi

# Create the cron command
CRON_COMMAND="cd $INSTALL_DIR && $INSTALL_DIR/venv/bin/python -m app.main >> $LOG_FILE 2>&1"

# Check if cron job already exists
echo -e "${YELLOW}Checking existing crontab...${NC}"
EXISTING_CRON=$(crontab -l 2>/dev/null || true)

if echo "$EXISTING_CRON" | grep -q "aissential-legal-agent"; then
    echo -e "${YELLOW}Warning: A cron job for aissential-legal-agent already exists${NC}"
    read -p "Do you want to replace it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cron setup cancelled"
        exit 0
    fi
    # Remove existing entry
    EXISTING_CRON=$(echo "$EXISTING_CRON" | grep -v "aissential-legal-agent")
fi

# Add the new cron job
echo -e "${YELLOW}Adding cron job...${NC}"
(echo "$EXISTING_CRON"; echo "# AIssential Legal Agent - runs every 30 minutes"; echo "$CRON_SCHEDULE $CRON_COMMAND") | crontab -

echo -e "${GREEN}Cron job added successfully!${NC}"
echo ""

# Display current crontab
echo -e "${YELLOW}Current crontab:${NC}"
echo "----------------------------------------"
crontab -l
echo "----------------------------------------"
echo ""

echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "The agent will run every 30 minutes."
echo "Logs will be written to: $LOG_FILE"
echo ""
echo "Useful commands:"
echo "  - View logs:        tail -f $LOG_FILE"
echo "  - Edit crontab:     sudo crontab -e"
echo "  - List cron jobs:   sudo crontab -l"
echo "  - Remove cron job:  sudo crontab -e (then delete the line)"
echo ""
