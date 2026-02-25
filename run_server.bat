@echo off
setlocal
call "%~dp0nearby_map\run.bat" server
exit /b %errorlevel%
