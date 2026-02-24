@echo off
setlocal
call "%~dp0nearby_map\run_validate.bat"
exit /b %errorlevel%
