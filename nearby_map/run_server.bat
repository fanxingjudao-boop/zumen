@echo off
setlocal
call "%~dp0run.bat" server
exit /b %errorlevel%
