@echo off
setlocal
cd /d "%~dp0"

py -m pip install -r requirements-build.txt
if errorlevel 1 goto :error

py -B -m unittest -v
if errorlevel 1 goto :error

py -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name "Simple RSS" ^
  --icon "simple_rss.ico" ^
  --add-data "simple_rss.ico;." ^
  --add-data "simple_rss.png;." ^
  simple_rss.py
if errorlevel 1 goto :error

echo.
echo Build complete. EXE is in the dist folder.
echo Launching Simple RSS for testing...
start "" "dist\Simple RSS.exe"
pause
exit /b 0

:error
echo.
echo Build failed.
pause
exit /b 1
