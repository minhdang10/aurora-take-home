#!/bin/bash

BASE_URL="http://localhost:8000"

echo "Testing Member Data QA System"
echo "=============================="
echo ""

# Test 1
echo "Question 1: When is Layla planning her trip to London?"
curl -X POST "${BASE_URL}/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "When is Layla planning her trip to London?"}'
echo ""
echo ""

# Test 2
echo "Question 2: How many cars does Vikram Desai have?"
curl -X POST "${BASE_URL}/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many cars does Vikram Desai have?"}'
echo ""
echo ""

# Test 3
echo "Question 3: What are Amira'\''s favorite restaurants?"
curl -X POST "${BASE_URL}/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are Amira'\''s favorite restaurants?"}'
echo ""
echo ""

echo "=============================="
echo "Tests complete!"

