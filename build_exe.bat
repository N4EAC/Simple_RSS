@echo off
setlocal
cd /d "%~dp0"

py -m pip install --upgrade pyinstaller
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
pause
exit /b 0

:error
echo.
echo Build failed.
pause
exit /b 1
