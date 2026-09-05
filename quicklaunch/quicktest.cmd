@echo off
rem ==============================================================================
rem RetinaAI Tele-Ophthalmology Platform - Quick Test Runner (Windows)
rem Smart India Hackathon (SIH) Prototype
rem Runs full test discovery (Unit Tests + Feature Tests + Diagnostic Self-Test)
rem ==============================================================================

setlocal enabledelayedexpansion

rem Resolve project root directory
if exist "%~dp0run_dashboard.py" (
    cd /d "%~dp0"
) else (
    cd /d "%~dp0.."
)
set PYTHONPATH=%CD%;%PYTHONPATH%

echo.
echo ======================================================
echo       RetinaAI Automated Test Suite Runner (QuickTest) 
echo       Smart India Hackathon (SIH) Prototype           
echo       Precision Clinical Tele-Ophthalmology System    
echo ======================================================
echo.

rem Check for Python interpreter
if exist "%CD%\.venv\Scripts\python.exe" (
    set PYTHON_CMD="%CD%\.venv\Scripts\python.exe"
) else if exist "%CD%\venv\Scripts\python.exe" (
    set PYTHON_CMD="%CD%\venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if !ERRORLEVEL! equ 0 (
        set PYTHON_CMD=python
    ) else (
        where py >nul 2>nul
        if !ERRORLEVEL! equ 0 (
            set PYTHON_CMD=py
        ) else (
            echo [ERROR] Python was not found in PATH.
            echo Please install Python 3.8+ and check "Add Python to PATH".
            pause
            exit /b 1
        )
    )
)

echo [1/3] Using Python:
%PYTHON_CMD% --version

echo.
echo [2/3] Running System Diagnostic Self-Test...
%PYTHON_CMD% run_dashboard.py --test

echo.
echo [3/3] Running Full Test Suite (Unit ^& Feature Tests)...
%PYTHON_CMD% -m unittest discover -s tests -v
set TEST_STATUS=%ERRORLEVEL%

echo.
if %TEST_STATUS% equ 0 (
    echo ======================================================
    echo    [PASS] ALL RETINAAI TESTS ^& DIAGNOSTICS PASSED!   
    echo ======================================================
) else (
    echo ======================================================
    echo    [FAIL] SOME TESTS FAILED (Exit Code: %TEST_STATUS%)
    echo ======================================================
)

pause
exit /b %TEST_STATUS%
