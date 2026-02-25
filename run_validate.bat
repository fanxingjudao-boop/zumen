@echo off
setlocal
call "%~dp0nearby_map\run.bat" validate
exit /b %errorlevel%
