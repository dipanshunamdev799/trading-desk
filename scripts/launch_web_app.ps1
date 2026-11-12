[CmdletBinding()]
param([switch]$NoBrowser, [switch]$Stop)

$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$logDir = Join-Path $root 'data\logs'
$statePath = Join-Path $logDir 'services.json'
$apiUrl = 'http://127.0.0.1:8000'
$webUrl = 'http://localhost:3000'
Set-Location -LiteralPath $root
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$services = @{}
if (Test-Path -LiteralPath $statePath) {
    $saved = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    foreach ($item in $saved.PSObject.Properties) { $services[$item.Name] = $item.Value }
}

function Save-Service($name, $process) {
    $services[$name] = @{ id = $process.Id; started = $process.StartTime.ToUniversalTime().ToString('o') }
    if ($name -eq 'web') {
        $services[$name].build_id = (Get-Content -LiteralPath (Join-Path $root 'frontend\.next\BUILD_ID') -Raw).Trim()
    }
    $services | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
}

function Test-OwnedProcess($entry, $process) {
    if (-not $entry -or -not $process) { return $false }
    try {
        $recordedStart = ([DateTimeOffset]$entry.started).UtcDateTime.Ticks
        return $process.StartTime.ToUniversalTime().Ticks -eq $recordedStart
    } catch { return $false }
}

function Stop-OwnedWeb {
    $entry = $services['web']
    if (-not $entry) { return $false }
    $process = Get-Process -Id $entry.id -ErrorAction SilentlyContinue
    if (-not (Test-OwnedProcess $entry $process)) { return $false }
    Write-Host '      Restarting the managed frontend to repair its build/assets...'
    & taskkill.exe /PID $process.Id /T /F | Out-Host
    if ($LASTEXITCODE -ne 0) { throw 'Could not stop the managed frontend for rebuild.' }
    $services.Remove('web')
    $services | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
    return $true
}

if ($Stop) {
    foreach ($name in @($services.Keys)) {
        $entry = $services[$name]
        $process = Get-Process -Id $entry.id -ErrorAction SilentlyContinue
        # A recycled PID must never cause an unrelated app to be stopped.
        if (Test-OwnedProcess $entry $process) {
            Write-Host "Stopping Trading Desk $name..."
            & taskkill.exe /PID $process.Id /T /F | Out-Host
        }
    }
    if (Test-Path -LiteralPath $statePath) { Remove-Item -LiteralPath $statePath }
    Write-Host 'Trading Desk services stopped. Database and stored data are preserved.'
    exit 0
}

function Get-ContentHash($path) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return [BitConverter]::ToString($sha.ComputeHash([IO.File]::ReadAllBytes((Resolve-Path $path).Path))) }
    finally { $sha.Dispose() }
}

function Invoke-Logged($exe, [string[]]$commandArgs, $logPath) {
    # Windows PowerShell treats native stderr as an ErrorRecord. Capture it
    # without terminating before the native exit code can be checked.
    $ErrorActionPreference = 'Continue'
    & $exe @commandArgs *> $logPath
    $script:nativeExit = $LASTEXITCODE
}

function Get-Json($url) {
    try { Invoke-RestMethod -Uri $url -TimeoutSec 3 } catch { $null }
}

function Test-Api {
    $health = Get-Json "$apiUrl/health"
    $identity = Get-Json "$apiUrl/"
    return ($health.ok -eq $true -and $health.database -eq 'ok' -and $identity.name -eq 'Trading Desk API')
}

function Test-Web {
    try {
        $page = Invoke-WebRequest -UseBasicParsing -Uri $webUrl -TimeoutSec 5
        $health = Get-Json "$webUrl/api/health"
        if ($page.StatusCode -ne 200 -or -not $page.Content.Contains('<title>Trading Desk</title>') -or $health.ok -ne $true) { return $false }
        $buildIdPath = Join-Path $root 'frontend\.next\BUILD_ID'
        if ($services['web'].build_id -and (Test-Path -LiteralPath $buildIdPath) -and $services['web'].build_id -ne (Get-Content -LiteralPath $buildIdPath -Raw).Trim()) { return $false }
        Invoke-Logged $python @((Join-Path $root 'scripts\check_web_assets.py'), '--url', $webUrl) (Join-Path $logDir 'web-assets.log')
        return $nativeExit -eq 0
    } catch { return $false }
}

function Assert-PortFree($port) {
    $listener = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners() | Where-Object { $_.Port -eq $port }
    if ($listener) {
        throw "Port $port is already occupied by an unready or different application. Stop that process, or use stop_web_app.bat for services started by this launcher, then launch again."
    }
}

function Wait-Service($name, $check, $process, $seconds) {
    $deadline = (Get-Date).AddSeconds($seconds)
    while ((Get-Date) -lt $deadline) {
        if (& $check) { return }
        $process.Refresh()
        if ($process.HasExited) { throw "$name exited with code $($process.ExitCode). See $logDir\$name.stderr.log" }
        Start-Sleep -Seconds 1
    }
    throw "$name did not become ready within $seconds seconds. See $logDir\$name.stderr.log"
}

try {
    Write-Host "Trading Desk - $root"
    $python = Join-Path $root '.venv\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $python)) {
        $bootstrap = Get-Command python.exe -ErrorAction SilentlyContinue
        if (-not $bootstrap) { throw 'Install Python 3.11 or newer and add python.exe to PATH.' }
        Invoke-Logged $bootstrap.Source @('-m', 'venv', (Join-Path $root '.venv')) (Join-Path $logDir 'venv.log')
        if ($nativeExit -ne 0) { throw 'Could not create the Python virtual environment.' }
    }
    $npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if (-not $npm) { throw 'Install Node.js 20 or newer (including npm), then launch again.' }

    Write-Host '[1/5] Checking backend dependencies...'
    $requirements = Join-Path $root 'backend\requirements.txt'
    $requirementsHash = (Get-ContentHash $requirements)
    $pipStamp = Join-Path $root '.venv\requirements.sha256'
    if (-not (Test-Path $pipStamp) -or (Get-Content $pipStamp -Raw).Trim() -ne $requirementsHash) {
        Invoke-Logged $python @('-m', 'pip', 'install', '--disable-pip-version-check', '-r', $requirements) (Join-Path $logDir 'pip.log')
        if ($nativeExit -ne 0) { throw "Backend dependency installation failed. See $logDir\pip.log" }
        Set-Content -LiteralPath $pipStamp -Value $requirementsHash
    }
    Invoke-Logged $python @('-m', 'pip', 'check') (Join-Path $logDir 'pip-check.log')
    if ($nativeExit -ne 0) { throw "Backend dependencies are inconsistent. See $logDir\pip-check.log" }

    Write-Host '[2/5] Checking database (existing data is preserved)...'
    $probe = "import sys; sys.path.insert(0, 'backend'); from sqlalchemy import create_engine, text; from app.config import get_settings; e=create_engine(get_settings().database_url_sync, connect_args={'connect_timeout': 3}); c=e.connect(); c.execute(text('SELECT 1')); c.close(); e.dispose()"
    Invoke-Logged $python @('-c', $probe) (Join-Path $logDir 'database.log')
    if ($nativeExit -ne 0) {
        $docker = Get-Command docker.exe -ErrorAction SilentlyContinue
        if (-not $docker) { throw 'Database is unavailable. Install/start Docker Desktop, or configure DATABASE_URL and DATABASE_URL_SYNC in .env.' }
        Invoke-Logged $docker.Source @('info') (Join-Path $logDir 'docker.log')
        if ($nativeExit -ne 0) { throw "Start Docker Desktop and wait for its engine to be ready, then launch again. See $logDir\docker.log" }
        Invoke-Logged $docker.Source @('compose', 'up', '-d', 'timescaledb') (Join-Path $logDir 'compose.log')
        if ($nativeExit -ne 0) { throw "Database startup failed. See $logDir\compose.log" }
        $deadline = (Get-Date).AddSeconds(90)
        do {
            Invoke-Logged $python @('-c', $probe) (Join-Path $logDir 'database.log')
            if ($nativeExit -eq 0) { break }
            Start-Sleep -Seconds 2
        } while ((Get-Date) -lt $deadline)
        if ($nativeExit -ne 0) { throw "Database did not become ready. See $logDir\database.log" }
    } else { Write-Host '      Using the available configured database.' }

    Write-Host '[3/5] Starting API and applying database migrations...'
    if (Test-Api) { Write-Host "      API already healthy at $apiUrl" } else {
        Assert-PortFree 8000
        $process = Start-Process -FilePath $python -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--app-dir', 'backend', '--host', '127.0.0.1', '--port', '8000') -WorkingDirectory $root -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logDir 'api.stdout.log') -RedirectStandardError (Join-Path $logDir 'api.stderr.log')
        Save-Service 'api' $process
        Wait-Service 'api' { Test-Api } $process 90
    }

    Write-Host '[4/5] Checking frontend...'
    if (Test-Web) { Write-Host "      Web app already healthy at $webUrl" } else {
        $restarted = Stop-OwnedWeb
        Assert-PortFree 3000
        Push-Location (Join-Path $root 'frontend')
        try {
            $lockHash = (Get-ContentHash 'package-lock.json')
            $npmStamp = 'node_modules\.trading-desk-lock.sha256'
            $install = -not (Test-Path 'node_modules')
            if (Test-Path $npmStamp) { $install = $install -or ((Get-Content $npmStamp -Raw).Trim() -ne $lockHash) }
            elseif (-not $install) {
                Invoke-Logged $npm.Source @('ls', '--depth=0') (Join-Path $logDir 'npm-check.log')
                $install = $nativeExit -ne 0
            }
            if ($install) {
                Write-Host '      Installing frontend dependencies...'
                Invoke-Logged $npm.Source @('ci') (Join-Path $logDir 'npm-install.log')
                if ($nativeExit -ne 0) { throw "Frontend installation failed. See $logDir\npm-install.log" }
            }
            Set-Content -LiteralPath $npmStamp -Value $lockHash
            Write-Host "      Building the web app. Progress: $logDir\web-build.log"
            Invoke-Logged $npm.Source @('run', 'build') (Join-Path $logDir 'web-build.log')
            if ($nativeExit -ne 0) { throw "Frontend build failed. See $logDir\web-build.log" }
            # Invoke node directly so its PID owns the complete web process tree.
            $node = (Get-Command node.exe).Source
            $process = Start-Process -FilePath $node -ArgumentList @('node_modules\next\dist\bin\next', 'start', '--hostname', '127.0.0.1', '--port', '3000') -WorkingDirectory (Get-Location).Path -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logDir 'web.stdout.log') -RedirectStandardError (Join-Path $logDir 'web.stderr.log')
            Save-Service 'web' $process
        } finally { Pop-Location }
        Wait-Service 'web' { Test-Web } $process 90
    }

    Write-Host '[5/5] Verifying the web-to-API connection...'
    if (-not (Test-Web)) { throw 'The web app cannot reach the healthy API through /api/health.' }
    $botStartup = Invoke-RestMethod -Uri "$apiUrl/trading-bots/startup" -Method Post -ContentType 'application/json' -Body '{}' -TimeoutSec 30
    Write-Host "Paper bots: $($botStartup.started.Count) start requests, $($botStartup.already_running.Count) already active, $($botStartup.skipped.Count) skipped, $($botStartup.failed.Count) failed."
    Write-Host "Ready: $webUrl"
    Write-Host "API docs: $apiUrl/docs"
    Write-Host "Logs: $logDir"
    Write-Host 'Run stop_web_app.bat to stop the app; the database keeps running.'
    if (-not $NoBrowser) { Start-Process $webUrl }
    exit 0
} catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Diagnostic logs: $logDir"
    exit 1
}
