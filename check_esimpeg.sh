#!/bin/bash

echo "=========================================="
echo "ESIMPEG API CONNECTION CHECK"
echo "=========================================="

# 1. Check .env file
echo ""
echo "1. Checking .env configuration:"
if [ -f .env ]; then
    echo "   ✅ .env file exists"
    echo "   ESIMPEG_API_URL=$(grep ESIMPEG_API_URL .env | cut -d '=' -f2)"
else
    echo "   ❌ .env file not found!"
fi

# 2. Check ESIMPEG container
echo ""
echo "2. Checking ESIMPEG container:"
if docker ps | grep -q esimpeg; then
    echo "   ✅ ESIMPEG container is running"
    docker ps | grep esimpeg | awk '{print "   Container:", $NF, "Status:", $(NF-1)}'
else
    echo "   ❌ ESIMPEG container is NOT running!"
    echo "   Start it with: docker start esimpeg_python_app"
fi

# 3. Check network connectivity
echo ""
echo "3. Checking network connectivity:"

# Get ESIMPEG URL from .env
ESIMPEG_URL=$(grep ESIMPEG_API_URL .env 2>/dev/null | cut -d '=' -f2 | tr -d ' ')

if [ -z "$ESIMPEG_URL" ]; then
    ESIMPEG_URL="http://localhost:8000"
    echo "   ⚠️ Using default URL: $ESIMPEG_URL"
else
    echo "   Using URL from .env: $ESIMPEG_URL"
fi

# Test health endpoint
echo "   Testing: $ESIMPEG_URL/health"
if curl -s -f -m 5 "$ESIMPEG_URL/health" > /dev/null 2>&1; then
    echo "   ✅ API is reachable!"
    curl -s "$ESIMPEG_URL/health" | python3 -m json.tool 2>/dev/null || echo ""
else
    echo "   ❌ Cannot reach API!"
    echo "   Possible issues:"
    echo "      - ESIMPEG is not running"
    echo "      - Wrong URL in .env"
    echo "      - Network/firewall issue"
fi

# 4. Test login endpoint
echo ""
echo "4. Testing login endpoint:"
echo "   Testing: $ESIMPEG_URL/apisimpeg/5.0/auth/login"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$ESIMPEG_URL/apisimpeg/5.0/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test"}' \
    -m 5 2>/dev/null)

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "404" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "400" ]; then
    echo "   ✅ Endpoint exists (Status: $HTTP_CODE)"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "   ❌ Cannot connect to endpoint"
else
    echo "   Status: $HTTP_CODE"
    echo "$BODY"
fi

# 5. Summary
echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="

# Check if everything is OK
ALL_OK=true

if [ ! -f .env ]; then
    ALL_OK=false
fi

if ! docker ps | grep -q esimpeg; then
    ALL_OK=false
fi

if ! curl -s -f -m 5 "$ESIMPEG_URL/health" > /dev/null 2>&1; then
    ALL_OK=false
fi

if [ "$ALL_OK" = true ]; then
    echo "✅ All checks passed!"
    echo ""
    echo "You can now test login at Survey Pemda:"
    echo "   URL: http://localhost:8006/"
    echo ""
    echo "If login still fails, check:"
    echo "   1. User exists in ESIMPEG database"
    echo "   2. Password is correct"
    echo "   3. User is active"
else
    echo "❌ Some checks failed!"
    echo ""
    echo "Fix the issues above and try again."
fi

echo ""
