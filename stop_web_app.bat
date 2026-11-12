@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch_web_app.ps1" -Stop
exit /b %ERRORLEVEL%
