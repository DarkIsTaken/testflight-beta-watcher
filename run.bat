@echo off
set SCRIPT_DIR=%~dp0
set PYTHON_PATH=python
set SCRIPT_PATH=%SCRIPT_DIR%testflight-beta-watcher.py
%PYTHON_PATH% %SCRIPT_PATH%
echo Script executed: %date% %time%
pause
