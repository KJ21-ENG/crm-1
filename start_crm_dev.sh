#!/bin/bash

# 🏢 Eshin Broking CRM Development Environment Startup Script
# This script starts all required services for Eshin Broking CRM development

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Updated for Eshin Broking
BENCH_PATH="/Volumes/MacSSD/Development/CursorAI_Project/frappe-bench"
CRM_PATH="$BENCH_PATH/apps/crm"

echo -e "${BLUE}🏢 Starting Eshin Broking CRM Development Environment...${NC}\n"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if service is running
check_service() {
    if pgrep -f "$1" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to wait for service to start
wait_for_service() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if check_service "$service"; then
            return 0
        fi
        sleep 1
        ((attempt++))
    done
    return 1
}

# 1. Start MariaDB
echo -e "${BLUE}📊 Starting MariaDB...${NC}"
if check_service "mariadb"; then
    print_warning "MariaDB already running"
else
    brew services start mariadb
    if wait_for_service "mariadb"; then
        print_status "MariaDB started successfully"
    else
        print_error "Failed to start MariaDB"
        exit 1
    fi
fi

# 2. Start Redis (default instance)
echo -e "${BLUE}🔄 Starting Redis (default)...${NC}"
if check_service "redis-server.*6379"; then
    print_warning "Redis (default) already running"
else
    brew services start redis
    if wait_for_service "redis-server.*6379"; then
        print_status "Redis (default) started successfully"
    else
        print_error "Failed to start Redis (default)"
        exit 1
    fi
fi

# 3. Navigate to bench directory
if [ ! -d "$BENCH_PATH" ]; then
    print_error "Bench directory not found: $BENCH_PATH"
    exit 1
fi

cd "$BENCH_PATH"
print_status "Changed to bench directory: $BENCH_PATH"

# 4. Start Redis Cache (port 13000)
echo -e "${BLUE}💾 Starting Redis Cache (port 13000)...${NC}"
if check_service "redis-server.*13000"; then
    print_warning "Redis Cache already running"
else
    redis-server config/redis_cache.conf --daemonize yes
    sleep 2
    if check_service "redis-server.*13000"; then
        print_status "Redis Cache started successfully"
    else
        print_error "Failed to start Redis Cache"
        exit 1
    fi
fi

# 5. Start Redis Queue (port 11000)
echo -e "${BLUE}📋 Starting Redis Queue (port 11000)...${NC}"
if check_service "redis-server.*11000"; then
    print_warning "Redis Queue already running"
else
    redis-server config/redis_queue.conf --daemonize yes
    sleep 2
    if check_service "redis-server.*11000"; then
        print_status "Redis Queue started successfully"
    else
        print_error "Failed to start Redis Queue"
        exit 1
    fi
fi

# 5.1. Configure Redis instances to prevent disk persistence issues
echo -e "${BLUE}🔧 Configuring Redis instances...${NC}"
redis-cli -p 11000 CONFIG SET stop-writes-on-bgsave-error no > /dev/null 2>&1
redis-cli -p 13000 CONFIG SET stop-writes-on-bgsave-error no > /dev/null 2>&1
print_status "Redis instances configured successfully"

# 6. Check if bench is already running
echo -e "${BLUE}🏗️  Checking Frappe Bench status...${NC}"
if check_service "frappe.*serve.*8000"; then
    print_warning "Frappe Bench already running"
    BENCH_RUNNING=true
else
    BENCH_RUNNING=false
fi

# 7. Check if frontend dev server is running
echo -e "${BLUE}🎨 Checking Frontend Dev Server status...${NC}"
if check_service "node.*vite"; then
    print_warning "Frontend Dev Server already running"
    FRONTEND_RUNNING=true
else
    FRONTEND_RUNNING=false
fi

# 8. Start Frappe Bench if not running
if [ "$BENCH_RUNNING" = false ]; then
    echo -e "${BLUE}🏗️  Starting Frappe Bench...${NC}"
    # Create a detached screen session for bench
    screen -dmS frappe_bench bash -c "cd '$BENCH_PATH' && bench start"
    sleep 5
    if check_service "frappe.*serve.*8000"; then
        print_status "Frappe Bench started in background (screen session: frappe_bench)"
    else
        print_error "Failed to start Frappe Bench"
        exit 1
    fi
fi

# 9. Start Frontend Dev Server if not running
if [ "$FRONTEND_RUNNING" = false ]; then
    echo -e "${BLUE}🎨 Starting Frontend Dev Server...${NC}"
    if [ ! -d "$CRM_PATH" ]; then
        print_error "CRM app directory not found: $CRM_PATH"
        exit 1
    fi
    
    # Create a detached screen session for frontend
    screen -dmS crm_frontend bash -c "cd '$CRM_PATH' && yarn dev"
    sleep 3
    if check_service "node.*vite"; then
        print_status "Frontend Dev Server started in background (screen session: crm_frontend)"
    else
        print_error "Failed to start Frontend Dev Server"
        exit 1
    fi
fi

# 10. Verify all services are running
echo -e "\n${BLUE}🔍 Verifying all services...${NC}"

services=(
    "mariadb:MariaDB Database"
    "redis-server.*6379:Redis Default"
    "redis-server.*11000:Redis Queue"
    "redis-server.*13000:Redis Cache"
    "frappe.*serve.*8000:Frappe Bench"
    "node.*vite:Frontend Dev Server"
)

all_running=true
for service in "${services[@]}"; do
    IFS=':' read -r process_name display_name <<< "$service"
    if check_service "$process_name"; then
        print_status "$display_name is running"
    else
        print_error "$display_name is NOT running"
        all_running=false
    fi
done

if [ "$all_running" = true ]; then
    echo -e "\n${GREEN}🎉 SUCCESS! All services are running!${NC}\n"
    
    echo -e "${BLUE}📱 Access your CRM:${NC}"
    echo -e "   ${GREEN}🔥 Development (Hot Reload): ${NC}http://localhost:8080"
    echo -e "   ${GREEN}🌐 Production Build:         ${NC}http://127.0.0.1:8000/crm"
    echo -e "   ${GREEN}⚙️  Admin Panel:             ${NC}http://127.0.0.1:8000"
    
    echo -e "\n${BLUE}🔐 Login Credentials:${NC}"
    echo -e "   ${GREEN}Username: ${NC}Administrator"
    echo -e "   ${GREEN}Password: ${NC}admin"
    
    echo -e "\n${BLUE}📱 Useful Commands:${NC}"
    echo -e "   ${GREEN}View Bench Logs:    ${NC}screen -r frappe_bench"
    echo -e "   ${GREEN}View Frontend Logs: ${NC}screen -r crm_frontend"
    echo -e "   ${GREEN}Stop All Services:  ${NC}./stop_crm_dev.sh"
    echo -e "   ${GREEN}List Screen Sessions:${NC}screen -ls"
    
    # Optional: Open browser automatically
    read -p "$(echo -e ${YELLOW}🌐 Open CRM in browser automatically? [y/N]: ${NC})" -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sleep 2
        open "http://localhost:8080" 2>/dev/null || print_warning "Could not open browser automatically"
    fi
    
else
    echo -e "\n${RED}❌ Some services failed to start. Please check the logs.${NC}"
    exit 1
fi