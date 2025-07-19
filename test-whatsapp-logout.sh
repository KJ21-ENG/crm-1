#!/bin/bash

# Test script for WhatsApp logout functionality
echo "🧪 Testing WhatsApp Logout Functionality"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if local service is running
check_service() {
    echo -e "${YELLOW}📡 Checking if local WhatsApp service is running...${NC}"
    if curl -s http://localhost:3001/health > /dev/null; then
        echo -e "${GREEN}✅ Local WhatsApp service is running${NC}"
        return 0
    else
        echo -e "${RED}❌ Local WhatsApp service is not running${NC}"
        echo -e "${YELLOW}💡 Start the service with: cd local-whatsapp-service && npm start${NC}"
        return 1
    fi
}

# Function to test logout endpoint
test_logout() {
    echo -e "${YELLOW}🔄 Testing logout endpoint...${NC}"
    
    # Test logout
    response=$(curl -s -X POST http://localhost:3001/logout -H "Content-Type: application/json")
    
    if echo "$response" | grep -q '"success":true'; then
        echo -e "${GREEN}✅ Logout endpoint working correctly${NC}"
        echo "Response: $response"
        return 0
    else
        echo -e "${RED}❌ Logout endpoint failed${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Function to test QR code generation after logout
test_qr_after_logout() {
    echo -e "${YELLOW}📱 Testing QR code generation after logout...${NC}"
    
    # Wait a bit for the service to reinitialize
    sleep 3
    
    # Check if QR code is available
    response=$(curl -s http://localhost:3001/qr-code)
    
    if echo "$response" | grep -q '"qrCode"'; then
        echo -e "${GREEN}✅ QR code generated successfully after logout${NC}"
        return 0
    else
        echo -e "${RED}❌ QR code not generated after logout${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Function to test status endpoint
test_status() {
    echo -e "${YELLOW}📊 Testing status endpoint...${NC}"
    
    response=$(curl -s http://localhost:3001/status)
    echo "Status: $response"
    
    if echo "$response" | grep -q '"status"'; then
        echo -e "${GREEN}✅ Status endpoint working${NC}"
        return 0
    else
        echo -e "${RED}❌ Status endpoint failed${NC}"
        return 1
    fi
}

# Main test execution
main() {
    echo -e "${YELLOW}🚀 Starting WhatsApp Logout Tests${NC}"
    echo ""
    
    # Check if service is running
    if ! check_service; then
        exit 1
    fi
    
    echo ""
    
    # Test status
    if ! test_status; then
        exit 1
    fi
    
    echo ""
    
    # Test logout
    if ! test_logout; then
        exit 1
    fi
    
    echo ""
    
    # Test QR code after logout
    if ! test_qr_after_logout; then
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}🎉 All tests passed! Logout functionality is working correctly.${NC}"
    echo ""
    echo -e "${YELLOW}📋 Next steps:${NC}"
    echo "1. Open the Chrome extension popup"
    echo "2. Click 'Logout WhatsApp' button"
    echo "3. Verify that a new QR code appears"
    echo "4. Test scanning with a different WhatsApp account"
}

# Run the tests
main 