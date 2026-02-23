@echo off
setlocal

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 download_tiles.py --dry-run
  goto :eof
)

where python >nul 2>nul
if %errorlevel%==0 (
  python download_tiles.py --dry-run
  goto :eof
)

echo [ERROR] Python launcher (py) / python が見つかりません。
echo Python 3.10+ をインストールし、Add python.exe to PATH を有効にしてください。
exit /b 1
