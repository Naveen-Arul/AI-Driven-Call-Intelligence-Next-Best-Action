@echo off
REM Start Customer Voice Bot - Quick Launcher
REM This script starts both backend API and frontend server

echo ================================================
echo   Customer Voice Bot - Quick Launcher
echo ================================================
echo.

REM Check if backend is already running
echo [1/2] Starting Backend API Server...
echo.
start "Backend API" cmd /k "cd /d %~dp0\..\backend && python app.py"
timeout /t 3 /nobreak > nul

REM Start frontend server
echo [2/2] Starting Frontend Server...
echo.
start "Frontend Server" cmd /k "cd /d %~dp0 && python -m http.server 8080"
timeout /t 2 /nobreak > nul

echo.
echo ================================================
echo   Both servers started successfully!
echo ================================================
echo.
echo Backend API:  http://localhost:5000
echo Frontend UI:  http://localhost:8080
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak > nul

REM Open browser
start http://localhost:8080

echo.
echo To stop servers: Close the terminal windows
echo Press any key to exit this launcher...
pause > nul
