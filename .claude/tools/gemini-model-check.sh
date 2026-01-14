#!/bin/bash
# gemini-model-check.sh - Detect Gemini model downgrades
# AgentOS Core Tool - Available to all child projects
#
# Usage: ./tools/gemini-model-check.sh "prompt text" [required-model]
#
# This script invokes Gemini CLI with JSON output and validates that the
# correct model tier is used. If Gemini downgrades to a lower model due to
# quota exhaustion, the script aborts and reports the issue.
#
# Exit codes:
#   0 - Success (correct model used)
#   1 - Gemini CLI failed to execute
#   2 - Quota exhausted (429 error)
#   3 - Model downgrade detected

set -euo pipefail

# Parse arguments
PROMPT="$1"
REQUIRED_MODEL="${2:-gemini-3-pro-preview}"

# Invoke Gemini CLI with JSON output
result=$(gemini -p "$PROMPT" \
  --model "$REQUIRED_MODEL" \
  --output-format json 2>&1) || {
  echo "ERROR: Gemini CLI failed to execute" >&2
  echo "$result" >&2
  exit 1
}

# Check for 429 quota errors in raw output
if echo "$result" | grep -qE "429|Resource exhausted|quota"; then
  echo "ERROR: Quota exhausted (429 error)" >&2

  # Try to extract quota reset time if available
  reset_time=$(echo "$result" | grep -oP "reset.*?(\d{4}-\d{2}-\d{2})" | head -1 || echo "Unknown")
  echo "Next reset: $reset_time" >&2

  exit 2
fi

# Extract JSON portion (skip any non-JSON prefix like "Loaded cached credentials.")
json_output=$(echo "$result" | sed -n '/{/,$p')

# Parse models used from JSON stats
models_json=$(echo "$json_output" | jq -r '.stats.models // {}' 2>/dev/null) || {
  echo "ERROR: Failed to parse JSON response" >&2
  echo "Raw output:" >&2
  echo "$result" >&2
  exit 1
}

# Check for model downgrades
downgrade=false
models_used=()

while IFS= read -r model; do
  # Trim any trailing whitespace/CR/LF
  model=$(echo "$model" | tr -d '\r\n')

  models_used+=("$model")

  # Check if this model is NOT one of the allowed models
  # Allow: gemini-3-pro-preview, gemini-3-pro (stable), or the explicitly required model
  if [[ "$model" != "$REQUIRED_MODEL" && "$model" != "gemini-3-pro" && "$model" != "gemini-3-pro-preview" ]]; then
    echo "ERROR: Model downgrade detected!" >&2
    echo "Required: $REQUIRED_MODEL" >&2
    echo "Actually used: $model" >&2
    downgrade=true
  fi
done < <(echo "$models_json" | jq -r 'keys[]')

if [ "$downgrade" = true ]; then
  echo "All models used: ${models_used[*]}" >&2
  exit 3
fi

# Success - output positive model verification to stderr (for capture/logging)
echo "---GEMINI-MODEL-VERIFIED---" >&2
echo "Model: ${models_used[*]}" >&2
echo "Stats.models:" >&2
echo "$models_json" | jq -c '.' >&2
echo "---END-VERIFICATION---" >&2

# Extract and output response only (no JSON wrapper) to stdout
response=$(echo "$json_output" | jq -r '.response')
echo "$response"

exit 0
