#!/usr/bin/env bash
# ==============================================================================
# RetinaAI Tele-Ophthalmology Platform - Quick Test Runner (macOS / Linux)
# Smart India Hackathon (SIH) Prototype
# Runs full test discovery (Unit Tests + Feature Tests + Diagnostic Self-Test)
# ==============================================================================

set -e

# Resolve project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "${SCRIPT_DIR}/run_dashboard.py" ]; then
    PROJECT_DIR="${SCRIPT_DIR}"
else
    PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
fi
cd "${PROJECT_DIR}"

export PYTHONPATH="${PROJECT_DIR}:${PYTHONPATH:-}"

echo ""
echo "======================================================"
echo "      RetinaAI Automated Test Suite Runner (QuickTest) "
echo "      Smart India Hackathon (SIH) Prototype           "
echo "      Precision Clinical Tele-Ophthalmology System    "
echo "======================================================"
echo ""

# Find suitable Python interpreter
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
    echo "Please install Python 3.8+ to run RetinaAI tests."
    exit 1
fi

echo "[1/3] Using Python: $($PYTHON_CMD --version)"
echo ""

echo "[2/3] Running System Diagnostic Self-Test..."
$PYTHON_CMD run_dashboard.py --test
echo ""

echo "[3/3] Running Full Test Suite (Unit & Feature Tests)..."
$PYTHON_CMD -m unittest discover -s tests -v
TEST_STATUS=$?

echo ""
if [ $TEST_STATUS -eq 0 ]; then
    echo "======================================================"
    echo "   ✓ ALL RETINAAI TESTS & DIAGNOSTICS PASSED (100%)   "
    echo "======================================================"
else
    echo "======================================================"
    echo "   ✗ SOME TESTS FAILED (Exit Code: $TEST_STATUS)      "
    echo "======================================================"
fi

exit $TEST_STATUS
