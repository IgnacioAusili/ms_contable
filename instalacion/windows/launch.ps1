param(
    [ValidateSet("Start", "Stop")]
    [string] $Action = "Start"
)

$ErrorActionPreference = "Stop"
$AppDir = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $AppDir "python\python.exe"
$DataDir = Join-Path $env:LOCALAPPDATA "MSContable\data"
$LogsDir = Join-Path $env:LOCALAPPDATA "MSContable\logs"
$PidFile = Join-Path $DataDir "server.pid"
$Port = 8000

function Get-ManagedServer {
    param([int] $ProcessId)

    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $ProcessId" -ErrorAction SilentlyContinue

    if (-not $process) {
        return $null
    }

    if ($process.ExecutablePath -ne $Python) {
        return $null
    }

    if ($process.CommandLine -notlike "*-m waitress*" -or $process.CommandLine -notlike "*ms_contable.wsgi:application*") {
        return $null
    }

    return Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
}

function Stop-ManagedServer {
    if (-not (Test-Path $PidFile)) {
        return
    }

    $processId = 0
    if ([int]::TryParse((Get-Content $PidFile -Raw), [ref]$processId)) {
        $process = Get-ManagedServer -ProcessId $processId
        if ($process) {
            Stop-Process -Id $process.Id -Force
            $process.WaitForExit()
        }
    }

    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

function Show-StartupError {
    param([string] $Message)

    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show(
        $Message,
        "MS Contable",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    ) | Out-Null
}

if ($Action -eq "Stop") {
    Stop-ManagedServer
    exit 0
}

try {
    if (-not (Test-Path $Python)) {
        throw "No se encuentra el runtime de Python instalado. Reinstalá MS Contable."
    }

    New-Item -ItemType Directory -Force -Path $DataDir, $LogsDir | Out-Null

    $existingProcess = $null
    if (Test-Path $PidFile) {
        $processId = 0
        if ([int]::TryParse((Get-Content $PidFile -Raw), [ref]$processId)) {
            $existingProcess = Get-ManagedServer -ProcessId $processId
        }
    }

    if (-not $existingProcess) {
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue

        $env:MSCONTABLE_DATA_DIR = $DataDir
        $env:MSCONTABLE_LOG_DIR = $LogsDir
        $stdout = Join-Path $LogsDir "server.out.log"
        $stderr = Join-Path $LogsDir "server.err.log"

        $process = Start-Process `
            -FilePath $Python `
            -ArgumentList @("-m", "waitress", "--listen=127.0.0.1:$Port", "ms_contable.wsgi:application") `
            -WorkingDirectory $AppDir `
            -WindowStyle Hidden `
            -PassThru `
            -RedirectStandardOutput $stdout `
            -RedirectStandardError $stderr

        Set-Content -Path $PidFile -Value $process.Id -Encoding ASCII
    }

    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        if ($process -and $process.HasExited) {
            break
        }

        try {
            $response = Invoke-WebRequest `
                -Uri "http://127.0.0.1:$Port/admin/login/" `
                -UseBasicParsing `
                -TimeoutSec 1

            if ($response.StatusCode -eq 200 -and $response.Content.Contains("MS Contable")) {
                $ready = $true
                break
            }
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }

    if (-not $ready) {
        if ($process) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        }

        throw "MS Contable no pudo iniciar en el puerto $Port. Revisá los logs en $LogsDir."
    }

    Start-Process "http://127.0.0.1:$Port"
}
catch {
    Show-StartupError -Message $_.Exception.Message
    exit 1
}
