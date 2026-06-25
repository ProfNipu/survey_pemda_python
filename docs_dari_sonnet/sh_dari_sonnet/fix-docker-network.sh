#!/bin/bash
################################################################################
# Auto-Fix Docker Network - All-in-One Script
# 
# Purpose: Fix DisallowedHost error after laptop restart
# Usage:   ./scripts/fix-docker-network.sh [--install|--uninstall|--status]
#
# Options:
#   (no args)    - Run auto-fix now
#   --install    - Install systemd service (auto-run on boot)
#   --uninstall  - Remove systemd service
#   --status     - Check service status
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

################################################################################
# Function: Check Docker
################################################################################
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running!${NC}"
        echo "Please start Docker first."
        exit 1
    fi
}

################################################################################
# Function: Wait for containers
################################################################################
wait_for_containers() {
    echo "Waiting for containers to be ready..."
    
    for i in {1..30}; do
        if docker ps --filter name=esimpeg_python_app --filter status=running | grep -q esimpeg_python_app; then
            break
        fi
        sleep 2
    done
    
    sleep 5  # Extra wait for full startup
}

################################################################################
# Function: Get container IPs
################################################################################
get_container_ips() {
    ESIMPEG_IP=$(docker inspect esimpeg_python_app 2>/dev/null | grep -m 1 '"IPAddress"' | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -1)
    SURVEY_IP=$(docker inspect survey_pemda_python_app 2>/dev/null | grep -m 1 '"IPAddress"' | grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' | head -1)
    
    if [ -z "$ESIMPEG_IP" ]; then
        echo -e "${RED}❌ Cannot get ESIMPEG IP${NC}"
        exit 1
    fi
}

################################################################################
# Function: Test connectivity
################################################################################
test_connectivity() {
    echo ""
    echo "Testing connectivity..."
    
    # Test using IP
    HTTP_CODE=$(docker exec survey_pemda_python_app curl -s -o /dev/null -w "%{http_code}" http://${ESIMPEG_IP}:8000/health/ 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ Survey Pemda → ESIMPEG: OK${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Survey Pemda → ESIMPEG: HTTP $HTTP_CODE${NC}"
        return 1
    fi
}

################################################################################
# Function: Update .env
################################################################################
update_env() {
    local ENV_FILE="$PROJECT_ROOT/projects/survey_pemda_python/.env"
    
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${RED}❌ .env file not found: $ENV_FILE${NC}"
        exit 1
    fi
    
    CURRENT_URL=$(grep "^ESIMPEG_API_URL=" "$ENV_FILE" | cut -d'=' -f2)
    NEW_URL="http://${ESIMPEG_IP}:8000"
    
    echo ""
    echo "Current .env: $CURRENT_URL"
    echo "New IP:       $NEW_URL"
    
    if [ "$CURRENT_URL" = "$NEW_URL" ]; then
        echo -e "${GREEN}✅ IP unchanged, no update needed${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}⚠️  IP changed, updating .env...${NC}"
    
    # Backup
    cp "$ENV_FILE" "$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Update
    sed -i "s|^ESIMPEG_API_URL=.*|ESIMPEG_API_URL=$NEW_URL|" "$ENV_FILE"
    
    echo -e "${GREEN}✅ .env updated${NC}"
    
    # Restart Survey Pemda
    echo "Restarting Survey Pemda container..."
    docker restart survey_pemda_python_app > /dev/null 2>&1
    sleep 5
    
    echo -e "${GREEN}✅ Container restarted${NC}"
}

################################################################################
# Function: Run auto-fix
################################################################################
run_autofix() {
    echo "=============================================="
    echo "Auto-Fix Docker Network"
    echo "=============================================="
    
    check_docker
    echo -e "${GREEN}✅ Docker is running${NC}"
    
    wait_for_containers
    
    get_container_ips
    echo ""
    echo "Container IPs:"
    echo "  ESIMPEG:      $ESIMPEG_IP"
    echo "  Survey Pemda: $SURVEY_IP"
    
    update_env
    
    test_connectivity
    
    echo ""
    echo "=============================================="
    echo -e "${GREEN}✅ Auto-fix complete!${NC}"
    echo "=============================================="
}

################################################################################
# Function: Install systemd service
################################################################################
install_service() {
    echo "=============================================="
    echo "Install Auto-Fix Systemd Service"
    echo "=============================================="
    
    if [ "$EUID" -eq 0 ]; then
        echo -e "${RED}❌ Do not run as root!${NC}"
        echo "Run as normal user: $0 --install"
        exit 1
    fi
    
    local CURRENT_USER=$(whoami)
    local SERVICE_FILE="/tmp/docker-network-fix.service"
    
    # Create service file
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Auto-fix Docker Network for ESIMPEG and Survey Pemda
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=$CURRENT_USER
WorkingDirectory=$PROJECT_ROOT
ExecStart=$SCRIPT_DIR/fix-docker-network.sh
RemainAfterExit=yes
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    echo "Installing service..."
    sudo cp "$SERVICE_FILE" /etc/systemd/system/docker-network-fix.service
    sudo systemctl daemon-reload
    sudo systemctl enable docker-network-fix.service
    
    echo -e "${GREEN}✅ Service installed${NC}"
    
    # Test service
    echo ""
    echo "Testing service..."
    sudo systemctl start docker-network-fix.service
    sleep 2
    
    echo ""
    sudo systemctl status docker-network-fix.service --no-pager || true
    
    echo ""
    echo "=============================================="
    echo -e "${GREEN}✅ Installation complete!${NC}"
    echo "=============================================="
    echo ""
    echo "Service will run automatically on boot."
    echo ""
    echo "Commands:"
    echo "  Status: sudo systemctl status docker-network-fix.service"
    echo "  Logs:   sudo journalctl -u docker-network-fix.service -f"
    echo "  Stop:   sudo systemctl stop docker-network-fix.service"
}

################################################################################
# Function: Uninstall systemd service
################################################################################
uninstall_service() {
    echo "=============================================="
    echo "Uninstall Auto-Fix Service"
    echo "=============================================="
    
    if [ ! -f /etc/systemd/system/docker-network-fix.service ]; then
        echo -e "${YELLOW}⚠️  Service not installed${NC}"
        exit 0
    fi
    
    echo "Stopping and disabling service..."
    sudo systemctl stop docker-network-fix.service 2>/dev/null || true
    sudo systemctl disable docker-network-fix.service 2>/dev/null || true
    
    echo "Removing service file..."
    sudo rm -f /etc/systemd/system/docker-network-fix.service
    sudo systemctl daemon-reload
    
    echo -e "${GREEN}✅ Service uninstalled${NC}"
}

################################################################################
# Function: Check service status
################################################################################
check_status() {
    echo "=============================================="
    echo "Service Status"
    echo "=============================================="
    
    if [ ! -f /etc/systemd/system/docker-network-fix.service ]; then
        echo -e "${YELLOW}⚠️  Service not installed${NC}"
        echo ""
        echo "To install: $0 --install"
        exit 0
    fi
    
    sudo systemctl status docker-network-fix.service --no-pager || true
    
    echo ""
    echo "Recent logs:"
    sudo journalctl -u docker-network-fix.service -n 20 --no-pager || true
}

################################################################################
# Main
################################################################################
main() {
    case "${1:-}" in
        --install)
            install_service
            ;;
        --uninstall)
            uninstall_service
            ;;
        --status)
            check_status
            ;;
        --help|-h)
            echo "Usage: $0 [--install|--uninstall|--status]"
            echo ""
            echo "Options:"
            echo "  (no args)    - Run auto-fix now"
            echo "  --install    - Install systemd service (auto-run on boot)"
            echo "  --uninstall  - Remove systemd service"
            echo "  --status     - Check service status"
            echo "  --help       - Show this help"
            ;;
        "")
            run_autofix
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage"
            exit 1
            ;;
    esac
}

main "$@"
