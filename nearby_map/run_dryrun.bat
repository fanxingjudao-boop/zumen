@echo off
setlocal EnableExtensions
pushd "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 download_tiles.py --dry-run
  set "RC=%errorlevel%"
  popd
  exit /b %RC%
)

where python >nul 2>nul
if %errorlevel%==0 (
  python download_tiles.py --dry-run
  set "RC=%errorlevel%"
  popd
  exit /b %RC%
)

echo [ERROR] Python launcher (py) or python was not found.
echo Install Python 3.10+ and enable Add python.exe to PATH.
popd
exit /b 1
