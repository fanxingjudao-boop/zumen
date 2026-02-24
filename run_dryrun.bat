@echo off
setlocal
call "%~dp0nearby_map\run_dryrun.bat"
exit /b %errorlevel%
