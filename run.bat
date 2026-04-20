@echo off
REM Launcher dla grunt_to_NMT.py
REM Automatycznie używa Python z AppData\Local\Programs\Python\Python310

setlocal enabledelayedexpansion

set PYTHON_PATH=C:\Users\ventu\AppData\Local\Programs\Python\Python310\python.exe

if not exist "%PYTHON_PATH%" (
    echo ERROR: Python nie znaleziony w: %PYTHON_PATH%
    echo Zainstaluj Python 3.10+ z python.org
    pause
    exit /b 1
)

cd /d "%~dp0"

REM Uruchom skrypt z wszystkimi argumentami
"%PYTHON_PATH%" grunt_to_NMT.py %*

if errorlevel 1 (
    echo.
    echo BLAD! Sprawdz powysze komunikaty.
    pause
)
