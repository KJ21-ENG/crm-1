#!/bin/bash

# Test script for CRM WhatsApp Integration
echo "🧪 Testing CRM WhatsApp Integration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test functions
test_node_version() {
    echo -e "${BLUE}📋 Testing Node.js version...${NC}"
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_VERSION" -ge 16 ]; then
            echo -e "${GREEN}✅ Node.js version: $(node -v)${NC}"
            return 0
        else
            echo -e "${RED}❌ Node.js version too old: $(node -v) (need 16+)${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Node.js not installed${NC}"
        return 1
    fi
}

test_local_service() {
    echo -e "${BLUE}📋 Testing local WhatsApp service...${NC}"
    
    # Check if service is running
    if curl -s http://localhost:3001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Local service is running${NC}"
        
        # Test health endpoint
        HEALTH_RESPONSE=$(curl -s http://localhost:3001/health)
        if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
            echo -e "${GREEN}✅ Health check passed${NC}"
        else
            echo -e "${YELLOW}⚠️  Health check response: $HEALTH_RESPONSE${NC}"
        fi
        
        # Test status endpoint
        STATUS_RESPONSE=$(curl -s http://localhost:3001/status)
        if echo "$STATUS_RESPONSE" | grep -q "status"; then
            echo -e "${GREEN}✅ Status endpoint working${NC}"
            echo -e "${BLUE}   Status: $(echo "$STATUS_RESPONSE" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)${NC}"
        else
            echo -e "${YELLOW}⚠️  Status endpoint response: $STATUS_RESPONSE${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}❌ Local service not running on port 3001${NC}"
        echo -e "${YELLOW}💡 Start the service: cd apps/crm/local-whatsapp-service && ./start-service.sh${NC}"
        return 1
    fi
}

test_extension_files() {
    echo -e "${BLUE}📋 Testing Chrome extension files...${NC}"
    
    EXTENSION_DIR="apps/crm/whatsapp-extension"
    REQUIRED_FILES=("manifest.json" "background.js" "content.js" "popup.html" "popup.js")
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$EXTENSION_DIR/$file" ]; then
            echo -e "${GREEN}✅ $file exists${NC}"
        else
            echo -e "${RED}❌ $file missing${NC}"
            return 1
        fi
    done
    
    # Check manifest.json structure
    if grep -q '"manifest_version": 3' "$EXTENSION_DIR/manifest.json"; then
        echo -e "${GREEN}✅ manifest.json is valid${NC}"
    else
        echo -e "${RED}❌ manifest.json is invalid${NC}"
        return 1
    fi
    
    return 0
}

test_crm_connection() {
    echo -e "${BLUE}📋 Testing CRM connection...${NC}"
    
    # Test if CRM is accessible
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ CRM is accessible on localhost:8000${NC}"
        return 0
    elif curl -s https://crm.localhost > /dev/null 2>&1; then
        echo -e "${GREEN}✅ CRM is accessible on crm.localhost${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  CRM not accessible on standard ports${NC}"
        echo -e "${YELLOW}💡 Make sure CRM is running and accessible${NC}"
        return 1
    fi
}

test_whatsapp_web() {
    echo -e "${BLUE}📋 Testing WhatsApp Web accessibility...${NC}"
    
    if curl -s https://web.whatsapp.com > /dev/null 2>&1; then
        echo -e "${GREEN}✅ WhatsApp Web is accessible${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  WhatsApp Web not accessible${NC}"
        echo -e "${YELLOW}💡 Check internet connection${NC}"
        return 1
    fi
}

test_port_availability() {
    echo -e "${BLUE}📋 Testing port availability...${NC}"
    
    if lsof -i :3001 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Port 3001 is in use (service running)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Port 3001 is available${NC}"
        return 1
    fi
}

# Main test execution
echo "🚀 Starting integration tests..."
echo ""

# Run all tests
TESTS_PASSED=0
TESTS_TOTAL=0

test_node_version
TESTS_TOTAL=$((TESTS_TOTAL + 1))
if [ $? -eq 0 ]; then TESTS_PASSED=$((TESTS_PASSED + 1)); fi

test_port_availability
TESTS_TOTAL=$((TESTS_TOTAL + 1))
if [ $? -eq 0 ]; then TESTS_PASSED=$((TESTS_PASSED + 1)); fi

test_local_service
TESTS_TOTAL=$((TESTS_TOTAL + 1))
if [ $? -eq 0 ]; then TESTS_PASSED=$((TESTS_PASSED + 1)); fi

test_extension_files
TESTS_TOTAL=$((TESTS_TOTAL + 1))
if [ $? -eq 0 ]; then TESTS_PASSED=$((TESTS_PASSED + 1)); fi

test_crm_connection
TESTS_TOTAL=$((TESTS_TOTAL + 1))
if [ $? -eq 0 ]; then TESTS_PASSED=$((TESTS_PASSED + 1)); fi

test_whatsapp_web
TESTS_TOTAL=$((TESTS_TOTAL + 1))
if [ $? -eq 0 ]; then TESTS_PASSED=$((TESTS_PASSED + 1)); fi

# Results
echo ""
echo "📊 Test Results:"
echo -e "${BLUE}Tests passed: ${GREEN}$TESTS_PASSED${NC}/${BLUE}$TESTS_TOTAL${NC}"

if [ $TESTS_PASSED -eq $TESTS_TOTAL ]; then
    echo -e "${GREEN}🎉 All tests passed! Integration is ready.${NC}"
    echo ""
    echo "📋 Next steps:"
    echo "1. Install Chrome extension from apps/crm/whatsapp-extension/"
    echo "2. Open CRM in Chrome"
    echo "3. Click extension icon and connect WhatsApp"
    echo "4. Scan QR code with your phone"
    echo "5. Start sending messages!"
else
    echo -e "${YELLOW}⚠️  Some tests failed. Please fix the issues above.${NC}"
    echo ""
    echo "🔧 Common fixes:"
    echo "1. Install Node.js 16+ if missing"
    echo "2. Start local service: cd apps/crm/local-whatsapp-service && ./start-service.sh"
    echo "3. Check CRM is running"
    echo "4. Verify internet connection"
fi

echo ""
echo "📚 For detailed setup instructions, see: apps/crm/MULTI_USER_WHATSAPP_SETUP.md" 