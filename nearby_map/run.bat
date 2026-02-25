@echo off
setlocal EnableExtensions
pushd "%~dp0"

set "CMD=%~1"
if "%CMD%"=="" goto :usage

if /I "%CMD%"=="validate" goto :validate
if /I "%CMD%"=="dryrun" goto :dryrun
if /I "%CMD%"=="server" goto :server
if /I "%CMD%"=="download" goto :download
if /I "%CMD%"=="help" goto :usage

echo [ERROR] Unknown command: %CMD%
goto :usage

:validate
call :runpy validate_config.py
set "RC=%errorlevel%"
goto :end

:dryrun
call :runpy download_tiles.py --dry-run
set "RC=%errorlevel%"
goto :end

:server
call :runpy -m http.server 8000
set "RC=%errorlevel%"
goto :end

:download
shift
call :runpy download_tiles.py %*
set "RC=%errorlevel%"
goto :end

:runpy
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 %*
  exit /b %errorlevel%
)

where python >nul 2>nul
if %errorlevel%==0 (
  python %*
  exit /b %errorlevel%
)

echo [ERROR] Python launcher (py) or python was not found.
echo Install Python 3.10+ and enable Add python.exe to PATH.
exit /b 1

:usage
echo Usage:
echo   run.bat validate                ^(validate config^)
echo   run.bat dryrun                  ^(estimate tile count^)
echo   run.bat server                  ^(start local server on 8000^)
echo   run.bat download --yes          ^(run downloader with args^)
echo.
set "RC=1"

:end
popd
exit /b %RC%
