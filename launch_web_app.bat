@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================================
REM  Trading Desk — local launcher
REM  Starts TimescaleDB (Docker) + FastAPI backend + Next.js frontend
REM ============================================================================

set "ROOT=%~dp0"
cd /d "%ROOT%"

set "PG_PORT=5432"
set "API_PORT=8000"
set "WEB_PORT=3000"
set "API_URL=http://127.0.0.1:%API_PORT%"
set "WEB_URL=http://127.0.0.1:%WEB_PORT%"

echo.
echo ============================================
echo   Trading Desk - starting local stack
echo   root: %ROOT%
echo ============================================
echo.

where docker >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Docker Desktop is not on PATH. Install/start Docker Desktop first.
  pause
  exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python is not on PATH.
  pause
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js / npm is not on PATH.
  pause
  exit /b 1
)

REM --- 1. TimescaleDB ---------------------------------------------------------
echo [1/5] Starting PostgreSQL + TimescaleDB via Docker Compose...
docker compose up -d
if errorlevel 1 (
  echo [ERROR] docker compose up failed.
  pause
  exit /b 1
)

echo       Waiting for database to accept connections...
set /a "WAITED=0"
:wait_db
docker compose exec -T timescaledb pg_isready -U trading -d trading >nul 2>nul
if not errorlevel 1 goto db_ready
set /a "WAITED+=1"
if !WAITED! GEQ 40 (
  echo [ERROR] Database did not become ready in time.
  pause
  exit /b 1
)
timeout /t 2 /nobreak >nul
goto wait_db
:db_ready
echo       Database ready.

REM --- 2. Backend venv + deps -------------------------------------------------
set "VENV=%ROOT%.venv"
set "PY_EXE=%ROOT%.venv\Scripts\python.exe"
if not exist "%PY_EXE%" (
  echo [2/5] Creating Python venv...
  python -m venv "%VENV%"
  if errorlevel 1 (
    echo [ERROR] Failed to create venv.
    pause
    exit /b 1
  )
) else (
  echo [2/5] Using existing venv.
)

echo       Installing backend dependencies...
"%PY_EXE%" -m pip install --disable-pip-version-check -q -r "%ROOT%backend\requirements.txt"
if errorlevel 1 (
  echo [WARN] pip install reported issues. Continuing with current venv packages.
)

REM --- 3. Frontend deps -------------------------------------------------------
echo [3/5] Installing frontend dependencies (npm)...
if not exist "%ROOT%frontend\node_modules" (
  pushd "%ROOT%frontend"
  call npm install
  if errorlevel 1 (
    echo [ERROR] npm install failed.
    popd
    pause
    exit /b 1
  )
  popd
) else (
  echo       node_modules already present.
)

REM --- 4. Start backend -------------------------------------------------------
echo [4/5] Starting FastAPI on %API_URL% ...
if not exist "%ROOT%data" mkdir "%ROOT%data"
if not exist "%ROOT%backtests" mkdir "%ROOT%backtests"

start "TradingDesk-API" /min "%PY_EXE%" -m uvicorn app.main:app --app-dir "%ROOT%backend" --host 127.0.0.1 --port %API_PORT%

set /a "WAITED=0"
:wait_api
powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 '%API_URL%/health' | Out-Null; exit 0 } catch { exit 1 }"
if not errorlevel 1 goto api_ready
set /a "WAITED+=1"
if !WAITED! GEQ 30 (
  echo [ERROR] Backend API did not come up. Check the TradingDesk-API window.
  pause
  exit /b 1
)
timeout /t 1 /nobreak >nul
goto wait_api
:api_ready
echo       API is healthy.

REM --- 5. Start frontend ------------------------------------------------------
echo [5/5] Starting Next.js on %WEB_URL% ...
pushd "%ROOT%frontend"
start "TradingDesk-Web" /min cmd /c "npm run dev"
popd

timeout /t 4 /nobreak >nul
start "" "%WEB_URL%"

echo.
echo ============================================
echo   Trading Desk is up
echo     Web  : %WEB_URL%
echo     API  : %API_URL%/docs
echo     DB   : 127.0.0.1:%PG_PORT%  (trading / trading)
echo.
echo   Close the TradingDesk-API / TradingDesk-Web
echo   windows to stop the app. Docker volume persists.
echo ============================================
echo.
pause
endlocal
