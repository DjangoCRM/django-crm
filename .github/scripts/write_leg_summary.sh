#!/usr/bin/env bash
set -euo pipefail

engine="${1:?engine name required}"
exit_code="${2:-1}"
log_file="${3:-test-output.log}"

{
  echo "## Test leg: ${engine}"
  echo ""
  echo "- **Engine:** \`${engine}\`"
  if [ "${exit_code}" -eq 0 ]; then
    echo "- **Status:** passed"
  else
    echo "- **Status:** failed"
    if [ -f "${log_file}" ]; then
      echo "- **Failing tests:**"
      echo '```'
      grep -E '^(FAIL|ERROR):' "${log_file}" | head -20 || true
      echo '```'
      failure_count="$(grep -Ec '^(FAIL|ERROR):' "${log_file}" || true)"
      if [ "${failure_count}" -gt 20 ]; then
        echo "_…and $((failure_count - 20)) more failures_"
      fi
    fi
  fi
} >> "${GITHUB_STEP_SUMMARY:?GITHUB_STEP_SUMMARY is not set}"
