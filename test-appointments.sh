#!/usr/bin/env bash

# Appointment System - Testing Script
# Utility to test the appointment system endpoints

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API_URL="${API_URL:-http://localhost:8000}"
API_BASE="${API_URL}/api/v1/appointments"

# Helper functions
print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Test: Health check
test_health() {
    print_header "Testing API Health"
    
    if response=$(curl -s "${API_URL}/docs" -o /dev/null -w "%{http_code}"); then
        if [ "$response" = "200" ]; then
            print_success "API is running on ${API_URL}"
            print_info "Swagger docs: ${API_URL}/docs"
        else
            print_error "API returned status code $response"
            return 1
        fi
    else
        print_error "Cannot connect to API at ${API_URL}"
        return 1
    fi
}

# Test: Create appointment
test_create() {
    print_header "Testing: Create Appointment"
    
    FUTURE_DATE=$(date -u -d "+3 days" +%Y-%m-%dT%H:%M:%S 2>/dev/null || date -u -v+3d +%Y-%m-%dT%H:%M:%S)
    
    echo -e "${YELLOW}Request:${NC}"
    echo "POST ${API_BASE}/"
    echo ""
    
    RESPONSE=$(curl -s -X POST "${API_BASE}/" \
        -H "Content-Type: application/json" \
        -d "{
            \"nombre\": \"Juan García Pérez\",
            \"email\": \"juan.garcia@test.com\",
            \"telefono\": \"+56912345678\",
            \"fecha\": \"${FUTURE_DATE}\",
            \"mensaje\": \"Reparación de KORG Micro Korg\"
        }")
    
    echo -e "${YELLOW}Response:${NC}"
    echo "$RESPONSE" | python3 -m json.tool
    
    # Extract ID for later tests
    APPOINTMENT_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null || echo "")
    
    if [ -n "$APPOINTMENT_ID" ] && [ "$APPOINTMENT_ID" != "null" ]; then
        print_success "Appointment created with ID: $APPOINTMENT_ID"
        echo "$APPOINTMENT_ID" > /tmp/appointment_id.txt
        return 0
    else
        print_error "Failed to create appointment"
        return 1
    fi
}

# Test: Get appointment
test_get() {
    print_header "Testing: Get Appointment"
    
    if [ ! -f /tmp/appointment_id.txt ]; then
        print_error "No appointment ID found. Run test_create first."
        return 1
    fi
    
    APPOINTMENT_ID=$(cat /tmp/appointment_id.txt)
    
    echo -e "${YELLOW}Request:${NC}"
    echo "GET ${API_BASE}/${APPOINTMENT_ID}"
    echo ""
    
    RESPONSE=$(curl -s -X GET "${API_BASE}/${APPOINTMENT_ID}")
    
    echo -e "${YELLOW}Response:${NC}"
    echo "$RESPONSE" | python3 -m json.tool
    
    print_success "Retrieved appointment $APPOINTMENT_ID"
}

# Test: List appointments
test_list() {
    print_header "Testing: List Appointments"
    
    echo -e "${YELLOW}Request:${NC}"
    echo "GET ${API_BASE}/?limit=5"
    echo ""
    
    RESPONSE=$(curl -s -X GET "${API_BASE}/?limit=5")
    
    echo -e "${YELLOW}Response:${NC}"
    echo "$RESPONSE" | python3 -m json.tool
    
    COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
    print_success "Found $COUNT appointments"
}

# Test: Get by email
test_by_email() {
    print_header "Testing: Get Appointments by Email"
    
    EMAIL="juan.garcia@test.com"
    
    echo -e "${YELLOW}Request:${NC}"
    echo "GET ${API_BASE}/email/${EMAIL}"
    echo ""
    
    RESPONSE=$(curl -s -X GET "${API_BASE}/email/${EMAIL}")
    
    echo -e "${YELLOW}Response:${NC}"
    echo "$RESPONSE" | python3 -m json.tool
}

# Test: Invalid input - bad nombre
test_invalid_nombre() {
    print_header "Testing: Invalid Input - Nombre with Numbers"
    
    FUTURE_DATE=$(date -u -d "+3 days" +%Y-%m-%dT%H:%M:%S 2>/dev/null || date -u -v+3d +%Y-%m-%dT%H:%M:%S)
    
    echo -e "${YELLOW}Request with INVALID nombre (should be rejected):${NC}"
    echo "POST ${API_BASE}/"
    echo ""
    
    RESPONSE=$(curl -s -X POST "${API_BASE}/" \
        -H "Content-Type: application/json" \
        -d "{
            \"nombre\": \"Juan123\",
            \"email\": \"test@test.com\",
            \"telefono\": \"+56912345678\",
            \"fecha\": \"${FUTURE_DATE}\"
        }")
    
    echo -e "${YELLOW}Response (should be validation error):${NC}"
    echo "$RESPONSE" | python3 -m json.tool
    
    if echo "$RESPONSE" | grep -q "validation"; then
        print_success "Validation correctly rejected invalid nombre"
    fi
}

# Test: Invalid input - bad email
test_invalid_email() {
    print_header "Testing: Invalid Input - Bad Email Format"
    
    FUTURE_DATE=$(date -u -d "+3 days" +%Y-%m-%dT%H:%M:%S 2>/dev/null || date -u -v+3d +%Y-%m-%dT%H:%M:%S)
    
    echo -e "${YELLOW}Request with INVALID email (should be rejected):${NC}"
    echo "POST ${API_BASE}/"
    echo ""
    
    RESPONSE=$(curl -s -X POST "${API_BASE}/" \
        -H "Content-Type: application/json" \
        -d "{
            \"nombre\": \"Juan García\",
            \"email\": \"invalidemail\",
            \"telefono\": \"+56912345678\",
            \"fecha\": \"${FUTURE_DATE}\"
        }")
    
    echo -e "${YELLOW}Response (should be validation error):${NC}"
    echo "$RESPONSE" | python3 -m json.tool
}

# Test: Invalid input - bad telefono
test_invalid_telefono() {
    print_header "Testing: Invalid Input - Teléfono without +"
    
    FUTURE_DATE=$(date -u -d "+3 days" +%Y-%m-%dT%H:%M:%S 2>/dev/null || date -u -v+3d +%Y-%m-%dT%H:%M:%S)
    
    echo -e "${YELLOW}Request with INVALID telefono (should be rejected):${NC}"
    echo "POST ${API_BASE}/"
    echo ""
    
    RESPONSE=$(curl -s -X POST "${API_BASE}/" \
        -H "Content-Type: application/json" \
        -d "{
            \"nombre\": \"Juan García\",
            \"email\": \"test@test.com\",
            \"telefono\": \"56912345678\",
            \"fecha\": \"${FUTURE_DATE}\"
        }")
    
    echo -e "${YELLOW}Response (should be validation error):${NC}"
    echo "$RESPONSE" | python3 -m json.tool
}

# Test: Invalid input - past date
test_invalid_date() {
    print_header "Testing: Invalid Input - Past Date"
    
    PAST_DATE=$(date -u -d "-1 days" +%Y-%m-%dT%H:%M:%S 2>/dev/null || date -u -v-1d +%Y-%m-%dT%H:%M:%S)
    
    echo -e "${YELLOW}Request with INVALID fecha (past date, should be rejected):${NC}"
    echo "POST ${API_BASE}/"
    echo ""
    
    RESPONSE=$(curl -s -X POST "${API_BASE}/" \
        -H "Content-Type: application/json" \
        -d "{
            \"nombre\": \"Juan García\",
            \"email\": \"test@test.com\",
            \"telefono\": \"+56912345678\",
            \"fecha\": \"${PAST_DATE}\"
        }")
    
    echo -e "${YELLOW}Response (should be validation error):${NC}"
    echo "$RESPONSE" | python3 -m json.tool
}

# Test: Get pending appointments
test_pending() {
    print_header "Testing: Get Pending Appointments"
    
    echo -e "${YELLOW}Request:${NC}"
    echo "GET ${API_BASE}/status/pending"
    echo ""
    
    RESPONSE=$(curl -s -X GET "${API_BASE}/status/pending")
    
    echo -e "${YELLOW}Response:${NC}"
    echo "$RESPONSE" | python3 -m json.tool
}

# Main menu
show_menu() {
    echo ""
    echo -e "${BLUE}Appointment System - Testing Menu${NC}"
    echo ""
    echo "1. Health check"
    echo "2. Create appointment (valid)"
    echo "3. Get appointment"
    echo "4. List appointments"
    echo "5. Get by email"
    echo "6. Test invalid nombre"
    echo "7. Test invalid email"
    echo "8. Test invalid telefono"
    echo "9. Test invalid date"
    echo "10. Get pending appointments"
    echo "11. Run all tests"
    echo "0. Exit"
    echo ""
}

# Run all tests
run_all_tests() {
    print_header "Running All Tests"
    
    test_health && \
    test_create && \
    test_get && \
    test_list && \
    test_by_email && \
    test_invalid_nombre && \
    test_invalid_email && \
    test_invalid_telefono && \
    test_invalid_date && \
    test_pending
    
    print_header "All Tests Completed"
}

# Main loop
if [ $# -eq 0 ]; then
    # Interactive mode
    while true; do
        show_menu
        read -p "Select option: " choice
        
        case $choice in
            1) test_health ;;
            2) test_create ;;
            3) test_get ;;
            4) test_list ;;
            5) test_by_email ;;
            6) test_invalid_nombre ;;
            7) test_invalid_email ;;
            8) test_invalid_telefono ;;
            9) test_invalid_date ;;
            10) test_pending ;;
            11) run_all_tests ;;
            0) echo "Exiting..."; exit 0 ;;
            *) echo "Invalid option"; continue ;;
        esac
        
        read -p "Press Enter to continue..."
    done
else
    # Command mode
    case $1 in
        health) test_health ;;
        create) test_create ;;
        get) test_get ;;
        list) test_list ;;
        email) test_by_email ;;
        invalid-nombre) test_invalid_nombre ;;
        invalid-email) test_invalid_email ;;
        invalid-telefono) test_invalid_telefono ;;
        invalid-date) test_invalid_date ;;
        pending) test_pending ;;
        all) run_all_tests ;;
        *)
            echo "Usage: $0 [health|create|get|list|email|invalid-nombre|invalid-email|invalid-telefono|invalid-date|pending|all]"
            echo ""
            echo "Examples:"
            echo "  $0 health        # Check if API is running"
            echo "  $0 create        # Create a test appointment"
            echo "  $0 list          # List all appointments"
            echo "  $0 all           # Run all tests"
            ;;
    esac
fi
