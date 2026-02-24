@echo off
setlocal
call "%~dp0nearby_map\run_server.bat"
exit /b %errorlevel%
