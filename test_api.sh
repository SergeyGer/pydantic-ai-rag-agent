#!/bin/bash
# test_api.sh - Script to test web scraping API

echo "=== Testing Web Scraping API ==="
echo

# Test 1: Load JSON from httpbin
echo "Test 1: Loading JSON from httpbin.org"
curl -X POST "http://localhost:8001/load_url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/json"}' \
  | python -m json.tool
echo
echo

# Test 2: Load HTML from httpbin
echo "Test 2: Loading HTML from httpbin.org"
curl -X POST "http://localhost:8001/load_url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html"}' \
  | python -m json.tool
echo
echo

# Test 3: Ask about loaded content
echo "Test 3: Asking about loaded content"
curl -X POST "http://localhost:8001/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What information did you load from the web?"}' \
  | python -m json.tool
echo
echo

# Test 4: Load from example.com
echo "Test 4: Loading from example.com"
curl -X POST "http://localhost:8001/load_url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}' \
  | python -m json.tool
echo
