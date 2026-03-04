@echo off
setlocal EnableExtensions DisableDelayedExpansion
 
REM ============================================================
REM        TRUE UNIVERSAL STREAMLIT LAUNCHER (WINDOWS)
REM  Works everywhere:
REM    ✔ python.exe (real install)
REM    ✔ py.exe launcher
REM    ✔ conda python
REM    ✔ existing venv
REM  Ignores fake Microsoft Store python
REM ============================================================
 
pushd "%~dp0" || (
    echo [ERROR] Cannot change directory to "%~dp0"
    pause
    exit /b 1
)
 
REM ---------------- CONFIG ----------------
set "APP_FILE=streamlit_app.py"
set "VENV_DIR=venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "REQ_FILE=requirements.txt"
 
echo [INFO] Working directory : "%CD%"
 
if not exist "%APP_FILE%" (
    echo [ERROR] Could not find "%APP_FILE%"
    echo [INFO] Candidates:
    dir /b "streamlit*.py"
    pause
    popd
    exit /b 1
)
 
REM ============================================================
REM            (A) DETECT PYTHON — UNIVERSAL LOGIC
REM ============================================================
 
set "PY_CMD="
 
REM 1) VENV Python (highest priority)
if exist "%VENV_PY%" (
    set "PY_CMD=%VENV_PY%"
    goto :PY_FOUND
)
 
REM 2) Real python.exe (ignore MS Store)
for /f "delims=" %%P in ('where python 2^>nul') do (
    echo %%P | findstr /i /v "WindowsApps" >nul
    if not errorlevel 1 (
        set "PY_CMD=%%P"
        goto :PY_FOUND
    )
)
 
REM 3) Python launcher (py.exe)
where py >nul 2>&1 && (
    set "PY_CMD=py -3"
    goto :PY_FOUND
)
 
REM 4) Conda python
where conda >nul 2>&1 && (
    for /f "delims=" %%D in ('conda info --base 2^>nul') do (
        if exist "%%D\python.exe" (
            set "PY_CMD=%%D\python.exe"
            goto :PY_FOUND
        )
    )
)
 
echo [ERROR] No valid Python installation found.
echo Install Python from https://www.python.org/downloads/
pause
popd
exit /b 1
 
:PY_FOUND
echo [INFO] Using Python: %PY_CMD%
 
 
REM ============================================================
REM            (B) CREATE VENV IF MISSING
REM ============================================================
 
if not exist "%VENV_PY%" (
    echo [INFO] Creating virtual environment "%VENV_DIR%" ...
    %PY_CMD% -m venv "%VENV_DIR%" || goto :FAIL_VENV
 
    echo [INFO] Upgrading pip...
    "%VENV_PY%" -m pip install --upgrade pip setuptools wheel || goto :FAIL_PIP
 
    if exist "%REQ_FILE%" (
        echo [INFO] Installing requirements.txt...
        "%VENV_PY%" -m pip install -r "%REQ_FILE%" || goto :FAIL_PIP
    ) else (
        echo [WARN] No requirements.txt found; skipping install.
    )
) else (
    echo [INFO] Existing venv detected.
)
 
REM ============================================================
REM            (C) ENSURE STREAMLIT INSTALLED
REM ============================================================
 
"%VENV_PY%" -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [INFO] Installing Streamlit...
    "%VENV_PY%" -m pip install streamlit || goto :FAIL_PIP
)
 
REM ============================================================
REM            (D) LAUNCH THE APP
REM ============================================================
 
echo [INFO] Launching "%APP_FILE%" on http://localhost:8501 ...
"%VENV_PY%" -m streamlit run "%APP_FILE%" ^
    --server.address=localhost ^
    --browser.gatherUsageStats=false
 
echo.
echo [INFO] Streamlit stopped.
pause
popd
exit /b 0
 
 
:FAIL_VENV
echo [ERROR] Virtual environment creation failed.
pause
popd
exit /b 1
 
:FAIL_PIP
echo [ERROR] pip installation failed.
pause
popd
exit /b 1