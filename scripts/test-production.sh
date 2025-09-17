#!/bin/bash
# Production Readiness Test Script
# Tests all critical functionality of the A2A Agent Registry

set -e

echo "🧪 A2A Agent Registry - Production Readiness Tests"
echo "=================================================="

BASE_URL=${BASE_URL:-"http://localhost:8000"}
DEMO_CLIENT_ID="demo-client"
DEMO_CLIENT_SECRET="demo-secret"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
log_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

test_endpoint() {
    local method=$1
    local endpoint=$2
    local expected_status=$3
    local description=$4
    local data=$5
    local headers=$6

    log_info "Testing: $description"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            ${headers:+-H "$headers"} \
            -d "$data")
    else
        response=$(curl -s -w "%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            ${headers:+-H "$headers"})
    fi
    
    status_code="${response: -3}"
    body="${response%???}"
    
    if [ "$status_code" -eq "$expected_status" ]; then
        log_success "$description - Status: $status_code"
        return 0
    else
        log_error "$description - Expected: $expected_status, Got: $status_code"
        echo "Response: $body"
        return 1
    fi
}

# Get OAuth token
get_oauth_token() {
    log_info "Getting OAuth token..."
    
    token_response=$(curl -s -X POST "$BASE_URL/oauth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "grant_type=password&username=$DEMO_CLIENT_ID&password=$DEMO_CLIENT_SECRET")
    
    if echo "$token_response" | grep -q "access_token"; then
        ACCESS_TOKEN=$(echo "$token_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
        log_success "OAuth token obtained"
        return 0
    else
        log_error "Failed to get OAuth token"
        echo "Response: $token_response"
        return 1
    fi
}

# Test 1: Health Checks
echo -e "\n🏥 Health Check Tests"
echo "===================="
test_endpoint "GET" "/health" 200 "Basic health check"
test_endpoint "GET" "/health/ready" 200 "Readiness check"
test_endpoint "GET" "/health/live" 200 "Liveness check"

# Test 2: Well-known endpoints
echo -e "\n🌐 Well-known Endpoints"
echo "======================"
test_endpoint "GET" "/.well-known/agents/index.json" 200 "Agents index"
test_endpoint "GET" "/.well-known/agent.json" 200 "Registry agent card"

# Test 3: Authentication
echo -e "\n🔐 Authentication Tests"
echo "======================="
if get_oauth_token; then
    test_endpoint "POST" "/oauth/introspect" 200 "Token introspection" "token=$ACCESS_TOKEN"
fi

# Test 4: Public Endpoints (no auth required)
echo -e "\n🌍 Public API Tests"
echo "==================="
test_endpoint "GET" "/agents/public" 200 "Public agents list"

# Test 5: Protected Endpoints (with auth)
if [ -n "$ACCESS_TOKEN" ]; then
    echo -e "\n🔒 Protected API Tests"
    echo "======================"
    
    AUTH_HEADER="Authorization: Bearer $ACCESS_TOKEN"
    
    test_endpoint "GET" "/agents" 200 "List agents (authenticated)" "" "$AUTH_HEADER"
    test_endpoint "GET" "/clients" 200 "List clients (authenticated)" "" "$AUTH_HEADER"
    test_endpoint "GET" "/peers" 200 "List peer registries (authenticated)" "" "$AUTH_HEADER"
    
    # Test agent search
    search_data='{"query": "test", "page": 1, "per_page": 10}'
    test_endpoint "POST" "/agents/search" 200 "Agent search" "$search_data" "$AUTH_HEADER"
fi

# Test 6: Security Headers
echo -e "\n🛡️  Security Headers Tests"
echo "=========================="

check_security_header() {
    local header_name=$1
    local expected_value=$2
    
    header_value=$(curl -s -I "$BASE_URL/health" | grep -i "$header_name" | cut -d':' -f2 | tr -d ' \r\n')
    
    if [ -n "$header_value" ]; then
        if [ -z "$expected_value" ] || [[ "$header_value" == *"$expected_value"* ]]; then
            log_success "Security header present: $header_name"
        else
            log_error "Security header incorrect: $header_name (Expected: $expected_value, Got: $header_value)"
        fi
    else
        log_error "Security header missing: $header_name"
    fi
}

check_security_header "X-Content-Type-Options" "nosniff"
check_security_header "X-Frame-Options" "DENY"
check_security_header "X-XSS-Protection" "1"
check_security_header "Strict-Transport-Security"
check_security_header "Content-Security-Policy"

# Test 7: Rate Limiting (basic test)
echo -e "\n⚡ Rate Limiting Tests"
echo "====================="

log_info "Testing rate limiting (making 10 rapid requests)..."
rate_limit_failures=0

for i in {1..10}; do
    status=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/health")
    if [ "$status" -eq 429 ]; then
        ((rate_limit_failures++))
    fi
done

if [ "$rate_limit_failures" -gt 0 ]; then
    log_success "Rate limiting is working (got $rate_limit_failures rate limit responses)"
else
    log_info "Rate limiting not triggered in basic test (may need higher load)"
fi

# Test 8: Error Handling
echo -e "\n🚨 Error Handling Tests"
echo "======================="
test_endpoint "GET" "/agents/nonexistent" 404 "Non-existent agent"
test_endpoint "GET" "/invalid-endpoint" 404 "Invalid endpoint"
test_endpoint "POST" "/agents" 401 "Unauthorized request (no token)"

# Test 9: Frontend Serving
echo -e "\n🎨 Frontend Tests"
echo "================="
test_endpoint "GET" "/" 200 "Frontend root"
test_endpoint "GET" "/login" 200 "Frontend login page"

# Summary
echo -e "\n📊 Test Summary"
echo "==============="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "\n🎉 ${GREEN}All tests passed! The application appears to be production-ready.${NC}"
    exit 0
else
    echo -e "\n⚠️  ${RED}Some tests failed. Please review the issues above before deploying to production.${NC}"
    exit 1
fi
