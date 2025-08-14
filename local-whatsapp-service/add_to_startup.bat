@echo off
REM Path to this folder
set "PROJECT_DIR=%~dp0"

REM Name of the script we want to run at startup
set "SCRIPT_NAME=start_project.bat"

REM Windows Startup folder for the current user
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

REM Create a shortcut (.lnk) in the Startup folder
echo Adding %SCRIPT_NAME% to Windows Startup...
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%STARTUP_FOLDER%\Start Project.lnk'); $s.TargetPath='%PROJECT_DIR%%SCRIPT_NAME%'; $s.WorkingDirectory='%PROJECT_DIR%'; $s.Save()"

echo Done! %SCRIPT_NAME% will now run automatically when Windows starts.
pause
