@echo off
REM Get the directory of this script
set "PROJECT_DIR=%~dp0"

REM Change to the project directory
cd /d "%PROJECT_DIR%"

REM Check if node_modules exists
if exist "node_modules" (
    echo Dependencies already installed, skipping npm install...
) else (
    echo Installing dependencies...
    npm install
)

REM Start the project
echo Starting the project...
npm start

pause
