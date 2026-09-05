@echo off
rem ==============================================================================
rem RetinaAI Tele-Ophthalmology Platform - Quick Launch Script (Windows)
rem Smart India Hackathon (SIH) Prototype
rem Design System: Precision Clinical (Terracotta #C2410C)
rem ==============================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0.."
set PYTHONPATH=%CD%;%PYTHONPATH%

set PORT=8000
if not "%~1"=="" set PORT=%~1

echo.
echo ======================================================
echo    RetinaAI Tele-Ophthalmology Dashboard Launcher    
echo    Smart India Hackathon (SIH) Prototype             
echo    Precision Clinical Tele-Ophthalmology System      
echo ======================================================
echo.

rem Check for Python
set PYTHON_CMD=
if exist "%CD%\.venv\Scripts\python.exe" (
    "%CD%\.venv\Scripts\python.exe" -c "import sys" >nul 2>nul
    if !ERRORLEVEL! equ 0 set PYTHON_CMD="%CD%\.venv\Scripts\python.exe"
)
if not defined PYTHON_CMD if exist "%CD%\venv\Scripts\python.exe" (
    "%CD%\venv\Scripts\python.exe" -c "import sys" >nul 2>nul
    if !ERRORLEVEL! equ 0 set PYTHON_CMD="%CD%\venv\Scripts\python.exe"
)
if not defined PYTHON_CMD (
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
echo [2/3] Running system diagnostics ^& contract verification...
%PYTHON_CMD% run_dashboard.py --test

rem Open default web browser after short pause
start "" http://localhost:%PORT%

echo.
echo [3/3] Starting RetinaAI Server on http://localhost:%PORT% ...
echo Press Ctrl+C in this window to stop the server.
echo.

%PYTHON_CMD% run_dashboard.py %PORT%

pause
