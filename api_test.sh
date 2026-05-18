#!/usr/bin/env bash
set -euo pipefail

BASE_URL=${BASE_URL:-http://localhost:8000}

curl -s "${BASE_URL}/api/stores" | cat
curl -s "${BASE_URL}/api/stats?store_id=1" | cat
curl -s "${BASE_URL}/api/inventory?store_id=1" | cat
curl -s "${BASE_URL}/api/forecast?store_id=1" | cat
curl -s "${BASE_URL}/api/messages?store_id=1&limit=20" | cat
