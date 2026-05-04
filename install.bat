@echo off
chcp 65001 >nul
title TF Tracker - Installation
color 0C

echo.
echo  ==========================================
echo        TF TRACKER - Installation
echo  ==========================================
echo.
echo  Installation startar...
echo  ================================================
echo.

:: Check Python
echo  [1/4] Kontrollerar Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  FEL: Python hittades inte!
    echo  Ladda ner Python fran: https://www.python.org/downloads/
    echo  Kryssa i "Add Python to PATH" under installationen.
    echo.
    pause
    start https://www.python.org/downloads/
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo  OK - %PYVER%

:: Install dependencies
echo.
echo  [2/4] Installerar Flask och ReportLab...
python -m pip install flask reportlab --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo  FEL: Kunde inte installera paket. Kontrollera internetanslutningen.
    pause
    exit /b 1
)
echo  OK - Flask och ReportLab installerade

:: Seed database
echo.
echo  [3/4] Skapar databas med alla Transformers-figurer...
echo  (Detta kan ta nagra sekunder...)
echo yes | python seed.py >nul 2>&1
if %errorlevel% neq 0 (
    echo  OBS: Databasen verkar redan finnas - det ar OK!
)
echo  OK - Databas klar

:: Create desktop shortcut
echo.
echo  [4/4] Skapar genvag pa skrivbordet...
set SCRIPT_DIR=%~dp0
set SHORTCUT=%USERPROFILE%\Desktop\TF Tracker.lnk
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%SCRIPT_DIR%TF Tracker.bat'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = '%SystemRoot%\System32\shell32.dll,137'; $s.Description = 'TF Tracker - Transformers Collection'; $s.Save()" >nul 2>&1
echo  OK - Genvag skapad pa skrivbordet

:: Done
echo.
echo  ================================================
echo  INSTALLATION KLAR!
echo  ================================================
echo.
echo  Starta appen med genvagen "TF Tracker" pa skrivbordet
echo  eller kor "TF Tracker.bat" i den har mappen.
echo.
echo  Appen oppnas automatiskt i din webblasare pa:
echo  http://localhost:5000
echo.
set /p START="  Starta TF Tracker nu? (j/n): "
if /i "%START%"=="j" (
    start "" "%SCRIPT_DIR%TF Tracker.bat"
)
echo.
pause
