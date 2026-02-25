@echo off
setlocal
call "%~dp0run.bat" validate
exit /b %errorlevel%
