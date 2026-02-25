@echo off
setlocal
call "%~dp0nearby_map\run.bat" dryrun
exit /b %errorlevel%
