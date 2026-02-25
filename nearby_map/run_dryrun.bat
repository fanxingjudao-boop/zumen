@echo off
setlocal
call "%~dp0run.bat" dryrun
exit /b %errorlevel%
