#!/usr/bin/env bash
# ==============================================================================
# RetinaAI Tele-Ophthalmology Platform - Quick Launch Script (macOS / Linux)
# Smart India Hackathon (SIH) Prototype
# Design System: Precision Clinical (Terracotta #C2410C)
# ==============================================================================

set -e

# Resolve project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_DIR}"

export PYTHONPATH="${PROJECT_DIR}:${PYTHONPATH:-}"

PORT="${1:-8000}"

echo ""
echo "======================================================"
echo "    RetinaAI Tele-Ophthalmology Dashboard Launcher    "
echo "    Smart India Hackathon (SIH) Prototype             "
echo "    Precision Clinical Tele-Ophthalmology System      "
echo "======================================================"
echo ""

# Find suitable Python interpreter
PYTHON_CMD=""
if [ -x "${PROJECT_DIR}/.venv/bin/python" ] && "${PROJECT_DIR}/.venv/bin/python" -c "import sys" >/dev/null 2>&1; then
    PYTHON_CMD="${PROJECT_DIR}/.venv/bin/python"
elif [ -x "${PROJECT_DIR}/venv/bin/python" ] && "${PROJECT_DIR}/venv/bin/python" -c "import sys" >/dev/null 2>&1; then
    PYTHON_CMD="${PROJECT_DIR}/venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python 3 was not found in PATH."
    echo "Please install Python 3.8+ to run RetinaAI."
    exit 1
fi

echo "[1/3] Using Python: $($PYTHON_CMD --version)"

# Run diagnostic self-test
echo "[2/3] Running system diagnostics & contract verification..."
$PYTHON_CMD run_dashboard.py --test

# Optional background browser open
(
    sleep 1.2
    URL="http://localhost:${PORT}"
    if command -v open >/dev/null 2>&1; then
        open "$URL"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$URL"
    fi
) &

echo ""
echo "[3/3] Starting RetinaAI Server on http://localhost:${PORT} ..."
echo "Press Ctrl+C to stop the server."
echo ""

exec $PYTHON_CMD run_dashboard.py "$PORT"
