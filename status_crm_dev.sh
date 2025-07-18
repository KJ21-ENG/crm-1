#!/bin/bash

# 📊 Frappe CRM Development Environment Status Checker
# This script shows the status of all CRM development services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📊 Frappe CRM Development Environment Status${NC}\n"

# Function to check if service is running
check_service() {
    if pgrep -f "$1" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to check multiple patterns (OR logic)
check_service_patterns() {
    local patterns="$1"
    if echo "$patterns" | grep -q "|"; then
        # Multiple patterns separated by |
        IFS='|' read -ra pattern_array <<< "$patterns"
        for pattern in "${pattern_array[@]}"; do
            if check_service "$pattern"; then
                return 0
            fi
        done
        return 1
    else
        # Single pattern
        check_service "$patterns"
    fi
}

# Check each service
services=(
    "mariadb:MariaDB Database:📊"
    "redis-server.*6379:Redis Default:🔄"
    "redis-server.*11001:Redis Queue:📋"
    "redis-server.*13001:Redis Cache:💾"
    "frappe.*serve.*8001|frappe.*socketio|bench.*serve:Frappe Bench:🏗️"
    "frappe.*schedule:Frappe Scheduler:⏰"
    "frappe.*worker.*default:Task Notification Worker:🔔"
    "node.*vite|esbuild:Frontend Dev Server:🎨"
    "node.*whatsapp-service.js:WhatsApp Service:📱"
)

echo -e "${BLUE}🔍 Service Status:${NC}"
all_running=true
for service in "${services[@]}"; do
    IFS=':' read -r process_patterns display_name icon <<< "$service"
    if check_service_patterns "$process_patterns"; then
        echo -e "   ${GREEN}${icon} ${display_name}: ✅ Running${NC}"
    else
        echo -e "   ${RED}${icon} ${display_name}: ❌ Stopped${NC}"
        all_running=false
    fi
done

echo ""

# Show URLs if services are running
if check_service_patterns "node.*vite|esbuild" || check_service_patterns "frappe.*serve.*8001|frappe.*socketio|bench.*serve"; then
    echo -e "${BLUE}📱 Access URLs:${NC}"
    if check_service_patterns "node.*vite|esbuild"; then
        echo -e "   ${GREEN}🔥 Development (Hot Reload): ${NC}http://localhost:5173"
    fi
    if check_service_patterns "frappe.*serve.*8001|frappe.*socketio|bench.*serve"; then
        echo -e "   ${GREEN}🌐 Backend Server:           ${NC}http://127.0.0.1:8001"
        echo -e "   ${GREEN}⚙️  Admin Panel:             ${NC}http://127.0.0.1:8001"
    fi
    echo ""
fi

# Show screen sessions
if command -v screen &> /dev/null; then
    echo -e "${BLUE}📺 Active Screen Sessions:${NC}"
    screen_sessions=$(screen -list 2>/dev/null | grep -E "(frappe_bench|frappe_scheduler|crm_worker|crm_frontend|crm_whatsapp)" | wc -l)
    if [ "$screen_sessions" -gt 0 ]; then
        screen -list 2>/dev/null | grep -E "(frappe_bench|frappe_scheduler|crm_worker|crm_frontend|crm_whatsapp)" | sed 's/^/   /'
    else
        echo -e "   ${YELLOW}No CRM screen sessions found${NC}"
    fi
    echo ""
fi

# Show detailed process info if some services are running
if [ "$all_running" = false ]; then
    echo -e "${BLUE}🔍 Process Details:${NC}"
    # Show what's currently running
    echo -e "${YELLOW}Currently running CRM processes:${NC}"
    ps aux | grep -E "(frappe.*serve|frappe.*schedule|frappe.*worker|vite|esbuild|redis-server.*1[13]001|mariadb|whatsapp-service)" | grep -v grep | head -10 | while read line; do
        echo "   $line"
    done
    echo ""
fi

# Overall status
if [ "$all_running" = true ]; then
    echo -e "${GREEN}🎉 Status: All services are running!${NC}"
    echo -e "${GREEN}💡 CRM is ready for development${NC}"
else
    echo -e "${YELLOW}⚠️  Status: Some services are not running${NC}"
    echo -e "${YELLOW}💡 Run ./start_crm_dev.sh to start all services${NC}"
fi

echo "" 