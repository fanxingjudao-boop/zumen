@echo off
setlocal

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -m http.server 8000
  goto :eof
)

where python >nul 2>nul
if %errorlevel%==0 (
  python -m http.server 8000
  goto :eof
)

echo [ERROR] Python launcher (py) / python が見つかりません。
echo Python 3.10+ をインストールし、Add python.exe to PATH を有効にしてください。
exit /b 1
