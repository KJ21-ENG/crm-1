#!/bin/bash

# 🏢 CRM Development Environment Startup Script
# This script starts all required services for CRM development

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BENCH_PATH="/Volumes/MacSSD/Development/CursorAI_Project/frappe-crm-bench"
CRM_PATH="$BENCH_PATH/apps/crm"

echo -e "${BLUE}🏢 Starting CRM Development Environment...${NC}\n"

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

# Kill existing processes
echo -e "${BLUE}🧹 Cleaning up existing processes...${NC}"
pkill -f "redis-server" || true
pkill -f "bench serve" || true
pkill -f "bench start" || true
pkill -f "yarn.*dev" || true
print_status "Cleanup completed"

# 1. Start Redis Cache
echo -e "${BLUE}💾 Starting Redis Cache...${NC}"
if check_service "redis-server.*13001"; then
    print_warning "Redis Cache already running"
else
    screen -dmS redis_cache bash -c "cd '$BENCH_PATH' && redis-server config/redis_cache.conf"
    if wait_for_service "redis-server.*13001"; then
        print_status "Redis Cache started successfully"
    else
        print_error "Failed to start Redis Cache"
        exit 1
    fi
fi

# 2. Start Redis Queue
echo -e "${BLUE}📋 Starting Redis Queue...${NC}"
if check_service "redis-server.*11001"; then
    print_warning "Redis Queue already running"
else
    screen -dmS redis_queue bash -c "cd '$BENCH_PATH' && redis-server config/redis_queue.conf"
    if wait_for_service "redis-server.*11001"; then
        print_status "Redis Queue started successfully"
    else
        print_error "Failed to start Redis Queue"
        exit 1
    fi
fi

# 3. Configure Redis instances
echo -e "${BLUE}🔧 Configuring Redis instances...${NC}"
redis-cli -p 13001 CONFIG SET stop-writes-on-bgsave-error no > /dev/null 2>&1
redis-cli -p 11001 CONFIG SET stop-writes-on-bgsave-error no > /dev/null 2>&1
print_status "Redis instances configured successfully"

# 4. Navigate to bench directory
if [ ! -d "$BENCH_PATH" ]; then
    print_error "Bench directory not found: $BENCH_PATH"
    exit 1
fi

cd "$BENCH_PATH"
print_status "Changed to bench directory: $BENCH_PATH"

# 5. Check if bench is already running
echo -e "${BLUE}🏗️  Checking Frappe Bench status...${NC}"
if check_service "bench serve.*8001"; then
    print_warning "Frappe Bench already running"
    BENCH_RUNNING=true
else
    BENCH_RUNNING=false
fi

# 6. Start Frappe Bench if not running
if [ "$BENCH_RUNNING" = false ]; then
    echo -e "${BLUE}🏗️  Starting Frappe Bench...${NC}"
    # Start bench with our specific configuration
    export FRAPPE_SITE=crm.localhost
    screen -dmS frappe_bench bash -c "cd '$BENCH_PATH' && bench serve --port 8001"
    sleep 5
    
    if check_service "bench serve.*8001"; then
        print_status "Frappe Bench started in background (screen session: frappe_bench)"
    else
        print_error "Failed to start Frappe Bench"
        exit 1
    fi
fi

# 7. Start Frontend Development Server
echo -e "${BLUE}🎨 Starting Frontend Dev Server...${NC}"
if check_service "yarn.*dev"; then
    print_warning "Frontend Dev Server already running"
else
    if [ ! -d "$CRM_PATH/frontend" ]; then
        print_error "Frontend directory not found: $CRM_PATH/frontend"
        exit 1
    fi
    
    # Create a detached screen session for frontend
    screen -dmS crm_frontend bash -c "cd '$CRM_PATH/frontend' && yarn && yarn dev"
    sleep 5
    if check_service "yarn.*dev"; then
        print_status "Frontend Dev Server started in background (screen session: crm_frontend)"
    else
        print_error "Failed to start Frontend Dev Server"
        exit 1
    fi
fi

# 8. Verify all services are running
echo -e "\n${BLUE}🔍 Verifying services...${NC}"

services=(
    "redis-server.*13001:Redis Cache"
    "redis-server.*11001:Redis Queue"
    "bench serve.*8001:Frappe Bench"
    "yarn.*dev:Frontend Dev Server"
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
    echo -e "   ${GREEN}🌐 Backend Server:     ${NC}http://192.168.1.71:8001"
    echo -e "   ${GREEN}🌐 Frontend Dev:       ${NC}http://192.168.1.71:5173"
    echo -e "   ${GREEN}🌐 Local Backend:      ${NC}http://127.0.0.1:8001"
    echo -e "   ${GREEN}🌐 Local Frontend:     ${NC}http://127.0.0.1:5173"
    
    echo -e "\n${BLUE}📱 Useful Commands:${NC}"
    echo -e "   ${GREEN}Redis Cache Logs:  ${NC}screen -r redis_cache"
    echo -e "   ${GREEN}Redis Queue Logs:  ${NC}screen -r redis_queue"
    echo -e "   ${GREEN}Backend Logs:      ${NC}screen -r frappe_bench"
    echo -e "   ${GREEN}Frontend Logs:     ${NC}screen -r crm_frontend"
    echo -e "   ${GREEN}List Sessions:     ${NC}screen -ls"
    echo -e "   ${GREEN}Stop All:          ${NC}pkill -f \"bench serve\"; pkill -f \"yarn.*dev\"; pkill -f \"redis-server\""
    
else
    echo -e "\n${RED}❌ Some services failed to start. Please check the logs.${NC}"
    exit 1
fi