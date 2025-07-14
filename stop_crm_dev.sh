#!/bin/bash

# 🛑 Frappe CRM Development Environment Stop Script
# This script stops all CRM development services gracefully

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛑 Stopping Frappe CRM Development Environment...${NC}\n"

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

# Function to stop Redis instance by port
stop_redis_port() {
    local port=$1
    local name=$2
    
    if check_service "redis-server.*${port}"; then
        # Try graceful shutdown first
        redis-cli -p ${port} shutdown save > /dev/null 2>&1
        sleep 1
        
        # If still running, try graceful shutdown without save
        if check_service "redis-server.*${port}"; then
            redis-cli -p ${port} shutdown nosave > /dev/null 2>&1
            sleep 1
        fi
        
        # If still running, force kill
        if check_service "redis-server.*${port}"; then
            pkill -f "redis-server.*${port}"
            sleep 1
        fi
        
        # If still running, use kill -9
        if check_service "redis-server.*${port}"; then
            pkill -9 -f "redis-server.*${port}"
            sleep 1
        fi
        
        # Verify it's stopped
        if ! check_service "redis-server.*${port}"; then
            print_status "${name} stopped"
        else
            print_error "Failed to stop ${name}"
        fi
    else
        print_warning "${name} was not running"
    fi
}

# 1. Stop Frontend Dev Server (screen session + processes)
echo -e "${BLUE}🎨 Stopping Frontend Dev Server...${NC}"
if screen -list | grep -q "crm_frontend"; then
    screen -S crm_frontend -X quit
    sleep 2
fi

# Kill any remaining vite/node processes
if check_service "node.*vite"; then
    pkill -f "node.*vite"
    sleep 1
fi

# Kill only CRM-related esbuild processes (avoid killing other projects)
esbuild_pids=$(ps aux | grep -E "esbuild.*crm|frappe-bench.*esbuild" | grep -v grep | awk '{print $2}')
if [ ! -z "$esbuild_pids" ]; then
    echo "Stopping CRM-related esbuild processes..."
    echo "$esbuild_pids" | xargs kill > /dev/null 2>&1
    sleep 2
    # Force kill if still running
    esbuild_pids=$(ps aux | grep -E "esbuild.*crm|frappe-bench.*esbuild" | grep -v grep | awk '{print $2}')
    if [ ! -z "$esbuild_pids" ]; then
        echo "$esbuild_pids" | xargs kill -9 > /dev/null 2>&1
        sleep 1
    fi
fi

if ! check_service "node.*vite" && ! ps aux | grep -E "esbuild.*crm|frappe-bench.*esbuild" | grep -v grep > /dev/null; then
    print_status "Frontend Dev Server stopped"
else
    print_warning "Some frontend processes still running"
fi

# 2. Stop Frappe Scheduler (screen session + processes)
echo -e "${BLUE}⏰ Stopping Frappe Scheduler...${NC}"
if screen -list | grep -q "frappe_scheduler"; then
    screen -S frappe_scheduler -X quit
    sleep 2
fi

if check_service "frappe.*schedule"; then
    pkill -f "frappe.*schedule"
    sleep 1
fi

if ! check_service "frappe.*schedule"; then
    print_status "Frappe Scheduler stopped"
else
    print_warning "Frappe Scheduler still running"
fi

# 3. Stop Task Notification Worker (screen session + processes)
echo -e "${BLUE}🔔 Stopping Task Notification Worker...${NC}"
if screen -list | grep -q "crm_worker"; then
    screen -S crm_worker -X quit
    sleep 2
fi

if check_service "frappe.*worker.*default"; then
    pkill -f "frappe.*worker.*default"
    sleep 1
fi

if ! check_service "frappe.*worker.*default"; then
    print_status "Task Notification Worker stopped"
else
    print_warning "Task Notification Worker still running"
fi

# 4. Stop Frappe Bench (screen session + processes)
echo -e "${BLUE}🏗️  Stopping Frappe Bench...${NC}"
if screen -list | grep -q "frappe_bench"; then
    screen -S frappe_bench -X quit
    sleep 2
fi

# Kill any remaining frappe processes more thoroughly
echo -e "${BLUE}🔄 Stopping remaining Frappe processes...${NC}"
frappe_patterns=(
    "frappe.*serve.*8001"
    "frappe.*socketio"
    "bench.*serve"
)

for pattern in "${frappe_patterns[@]}"; do
    if check_service "$pattern"; then
        pkill -f "$pattern"
        sleep 1
    fi
done

# Additional cleanup for any remaining bench processes
if check_service "bench serve"; then
    pkill -f "bench serve"
    sleep 1
fi

if ! check_service "frappe.*serve.*8001" && ! check_service "frappe.*socketio" && ! check_service "bench.*serve"; then
    print_status "Frappe Bench stopped"
else
    print_warning "Some Frappe processes still running"
fi

# 5. Stop Redis Queue (port 11001)
echo -e "${BLUE}📋 Stopping Redis Queue...${NC}"
stop_redis_port 11001 "Redis Queue"

# 6. Stop Redis Cache (port 13001)  
echo -e "${BLUE}💾 Stopping Redis Cache...${NC}"
stop_redis_port 13001 "Redis Cache"

# 7. Optionally stop default Redis and MariaDB
read -p "$(echo -e ${YELLOW}🔄 Stop Redis and MariaDB services too? [y/N]: ${NC})" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    
    echo -e "${BLUE}🔄 Stopping Redis (default)...${NC}"
    if check_service "redis-server.*6379"; then
        brew services stop redis
        sleep 1
        print_status "Redis (default) stopped"
    else
        print_warning "Redis (default) was not running"
    fi
    
    echo -e "${BLUE}📊 Stopping MariaDB...${NC}"
    if brew services list | grep mariadb | grep -q started; then
        brew services stop mariadb
        sleep 1
        print_status "MariaDB stopped"
    else
        print_warning "MariaDB was not running"
    fi
fi

# 8. Clean up any remaining screen sessions
echo -e "${BLUE}🧹 Cleaning up screen sessions...${NC}"
screen -wipe > /dev/null 2>&1

# 9. Final verification
echo -e "\n${BLUE}🔍 Verifying services are stopped...${NC}"

crm_services=(
    "node.*vite:Frontend Dev Server"
    "frappe.*serve.*8001|frappe.*socketio|bench.*serve:Frappe Bench"
    "frappe.*schedule:Frappe Scheduler"
    "frappe.*worker.*default:Task Notification Worker"
    "redis-server.*11001:Redis Queue"
    "redis-server.*13001:Redis Cache"
)

all_stopped=true
for service in "${crm_services[@]}"; do
    IFS=':' read -r process_pattern display_name <<< "$service"
    
    # Check if any of the patterns match
    found_process=false
    if echo "$process_pattern" | grep -q "|"; then
        # Multiple patterns separated by |
        IFS='|' read -ra patterns <<< "$process_pattern"
        for pattern in "${patterns[@]}"; do
            if check_service "$pattern"; then
                found_process=true
                break
            fi
        done
    else
        # Single pattern or special cases
        if [ "$process_pattern" = "node.*vite" ]; then
            # Check for both vite and CRM-specific esbuild
            if check_service "node.*vite" || ps aux | grep -E "esbuild.*crm|frappe-bench.*esbuild" | grep -v grep > /dev/null; then
                found_process=true
            fi
        else
            if check_service "$process_pattern"; then
                found_process=true
            fi
        fi
    fi
    
    if [ "$found_process" = false ]; then
        print_status "$display_name is stopped"
    else
        print_error "$display_name is still running"
        all_stopped=false
    fi
done

if [ "$all_stopped" = true ]; then
    echo -e "\n${GREEN}🎉 SUCCESS! All CRM development services stopped!${NC}"
    echo -e "${GREEN}💡 Run ./start_crm_dev.sh to start them again${NC}\n"
else
    echo -e "\n${YELLOW}⚠️  Some services are still running. You may need to stop them manually.${NC}"
    echo -e "${YELLOW}💡 Use 'ps aux | grep <service>' to find and 'kill <pid>' to stop manually${NC}\n"
    
    # Show what's still running
    echo -e "${YELLOW}🔍 Currently running processes:${NC}"
    ps aux | grep -E "(frappe|vite|esbuild|redis-server.*1[13]001)" | grep -v grep || echo "  None found"
    echo
fi 