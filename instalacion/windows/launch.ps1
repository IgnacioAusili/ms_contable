param(
    [ValidateSet("Start", "Stop")]
    [string] $Action = "Start",
    [string] $SplashSignalPath = "",
    [string] $SplashReadySignalPath = ""
)

$ErrorActionPreference = "Stop"
$InstallDir = Split-Path -Parent $PSScriptRoot
$AppDir = $InstallDir
$Python = Join-Path $InstallDir "python\python.exe"
$Caddy = Join-Path $InstallDir "caddy\caddy.exe"
$Caddyfile = Join-Path $InstallDir "caddy\Caddyfile"
$BootstrapScript = Join-Path $PSScriptRoot "bootstrap.py"
$SessionMonitorScript = Join-Path $PSScriptRoot "session-monitor.ps1"
$DataRoot = Join-Path $env:LOCALAPPDATA "MSContable"
$RuntimeCaddyfile = Join-Path $DataRoot "config\runtime.Caddyfile"
$DataDir = Join-Path $DataRoot "data"
$LogsDir = Join-Path $DataRoot "logs"
$CaddyDataHome = $DataRoot
$CaddyStorage = Join-Path $CaddyDataHome "caddy"
$RootCertificate = Join-Path $CaddyStorage "pki\authorities\local\root.crt"
$WaitressPidFile = Join-Path $DataDir "waitress.pid"
$CaddyPidFile = Join-Path $DataDir "caddy.pid"
$BootstrapPidFile = Join-Path $DataDir "bootstrap.pid"
$SessionTokenFile = Join-Path $DataDir "session-token"
$HeartbeatDir = Join-Path $DataDir "browser-sessions"
$DynamicPorts = @(49152..65535)
$BackendPortFile = Join-Path $DataDir "waitress.port"
$HttpsPortFile = Join-Path $DataDir "caddy.port"
$BackendPort = 0
$HttpsPort = 0
$SiteHost = "mscontable"
$startedWaitress = $null
$startedCaddy = $null
$bootstrapProcess = $null
$browserOpened = $false
$StateFile = $null
$PortFile = $null
$StartupClock = [System.Diagnostics.Stopwatch]::StartNew()
$StartupLog = Join-Path $LogsDir "startup.log"

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class MSContableWindowNative {
    [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr window, int command);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr window);
}
"@

. (Join-Path $PSScriptRoot "launch-support.ps1")
. $SessionMonitorScript

function Start-WaitressOnRandomPort {
    param([int] $Port)

    if (-not (Test-LocalPortAvailable -Port $Port)) {
        throw "El puerto aleatorio $Port dejó de estar disponible antes de iniciar Waitress. Volvé a abrir MS Contable para elegir otro."
    }

    Remove-Item $WaitressPidFile -Force -ErrorAction SilentlyContinue
    $process = Start-Process `
        -FilePath $Python `
        -ArgumentList @(
            "-m", "waitress", "--listen=127.0.0.1:$Port",
            "--trusted-proxy=127.0.0.1", "--trusted-proxy-headers=x-forwarded-proto",
            "ms_contable.wsgi:application"
        ) `
        -WorkingDirectory $AppDir `
        -WindowStyle Hidden `
        -PassThru `
        -RedirectStandardOutput $waitressStdout `
        -RedirectStandardError $waitressStderr
    $script:startedWaitress = $process
    Set-Content -Path $WaitressPidFile -Value $process.Id -Encoding ASCII
    Write-StartupLog -Message "Waitress iniciado en 127.0.0.1:$Port"

    $readyClock = [System.Diagnostics.Stopwatch]::StartNew()
    $serverReady = $false
    while ($readyClock.Elapsed.TotalSeconds -lt 25) {
        if ($process.HasExited) {
            break
        }
        try {
            $response = Invoke-WebRequest `
                -Uri "http://127.0.0.1:$Port/admin/login/" `
                -Headers @{ "X-Forwarded-Proto" = "https" } `
                -UseBasicParsing `
                -TimeoutSec 1
            if ($response.StatusCode -eq 200) {
                $serverReady = $true
                break
            }
        }
        catch {
            Start-Sleep -Milliseconds 250
        }
    }

    if (-not $serverReady) {
        $failureLog = if (Test-Path $waitressStderr) { [System.IO.File]::ReadAllText($waitressStderr) } else { "" }
        if (-not $process.HasExited) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
        Remove-Item $WaitressPidFile -Force -ErrorAction SilentlyContinue
        throw "Waitress no pudo iniciar en el puerto aleatorio $Port. $failureLog"
    }

    $script:BackendPort = $Port
    Set-Content -Path $BackendPortFile -Value $Port -Encoding ASCII
    return $process
}

function Start-CaddyOnRandomPort {
    param([int] $Port)

    if (-not (Test-LocalPortAvailable -Port $Port)) {
        throw "El puerto HTTPS aleatorio $Port dejó de estar disponible antes de iniciar Caddy. Volvé a abrir MS Contable para elegir otro."
    }

    Write-RuntimeCaddyfile -Path $RuntimeCaddyfile -HttpsPort $Port -BackendPort $BackendPort
    Remove-Item $CaddyPidFile -Force -ErrorAction SilentlyContinue
    $process = Start-Process `
        -FilePath $Caddy `
        -ArgumentList @("run", "--config", "`"$RuntimeCaddyfile`"", "--adapter", "caddyfile") `
        -WorkingDirectory (Split-Path -Parent $Caddy) `
        -WindowStyle Hidden `
        -PassThru `
        -RedirectStandardOutput $caddyStdout `
        -RedirectStandardError $caddyStderr
    $script:startedCaddy = $process
    Set-Content -Path $CaddyPidFile -Value $process.Id -Encoding ASCII

    try {
        Wait-ForCaddyCertificate -CaddyProcess $process -Port $Port -TimeoutSeconds 15
    }
    catch {
        $failureLog = if (Test-Path $caddyStderr) { [System.IO.File]::ReadAllText($caddyStderr) } else { "" }
        if (-not $process.HasExited) {
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
        Remove-Item $CaddyPidFile -Force -ErrorAction SilentlyContinue
        throw "Caddy no pudo iniciar en el puerto HTTPS aleatorio $Port. $failureLog"
    }

    $script:HttpsPort = $Port
    Set-Content -Path $HttpsPortFile -Value $Port -Encoding ASCII
    Write-StartupLog -Message "Caddy presentó HTTPS en el puerto aleatorio $Port"
    return $process
}

function Open-ExistingApplication {
    $existingPort = Read-ConfiguredPort -Path $HttpsPortFile -Default 0 -AllowedPorts $DynamicPorts
    if ($existingPort -le 0) {
        return $false
    }

    $existingUrl = "https://${SiteHost}:$existingPort/admin/login/"
    try {
        $response = Invoke-WebRequest -Uri $existingUrl -UseBasicParsing -TimeoutSec 3
        if ($response.StatusCode -ne 200) {
            return $false
        }
        $browserWindow = Get-Process -ErrorAction SilentlyContinue |
            Where-Object { $_.MainWindowHandle -ne [IntPtr]::Zero -and $_.MainWindowTitle -match "(?i)MS Contable" } |
            Select-Object -First 1

        if ($browserWindow) {
            [MSContableWindowNative]::ShowWindowAsync($browserWindow.MainWindowHandle, 9) | Out-Null
            [MSContableWindowNative]::SetForegroundWindow($browserWindow.MainWindowHandle) | Out-Null
            Write-StartupLog -Message "Se activó la ventana del navegador de la instancia existente; no se abrió otra pestaña"
            return $true
        }

        $browserLaunchRequest = Join-Path $DataDir "browser-launch-requested.utc"
        $recentLaunchRequest = $false
        if (Test-Path -LiteralPath $browserLaunchRequest -PathType Leaf) {
            $recentLaunchRequest = ([DateTime]::UtcNow - (Get-Item -LiteralPath $browserLaunchRequest).LastWriteTimeUtc).TotalSeconds -lt 15
        }
        if (-not $recentLaunchRequest) {
            Set-Content -LiteralPath $browserLaunchRequest -Value ([DateTime]::UtcNow.ToString("o")) -Encoding ASCII
            Start-Process $existingUrl
            Write-StartupLog -Message "Se abrió la página porque no había una ventana visible de MS Contable"
        }
        else {
            Write-StartupLog -Message "Se omitió una apertura repetida del navegador durante la carga"
        }
        return $true
    }
    catch {
        return $false
    }
}

if ($Action -eq "Stop") {
    Stop-ManagedProcess -PidFile $BootstrapPidFile -Executable $Python -CommandMarker "bootstrap.py"
    Stop-ManagedProcess -PidFile $CaddyPidFile -Executable $Caddy -CommandMarker @($RuntimeCaddyfile, $Caddyfile)
    Stop-ManagedProcess -PidFile $WaitressPidFile -Executable $Python -CommandMarker "ms_contable.wsgi:application"
    return
}

$launcherMutex = [System.Threading.Mutex]::new($false, "Local\MSContableLauncher")
$ownsLauncherMutex = $false
try {
    try {
        $ownsLauncherMutex = $launcherMutex.WaitOne(0)
    }
    catch [System.Threading.AbandonedMutexException] {
        $ownsLauncherMutex = $true
    }

    if (-not $ownsLauncherMutex) {
        Open-ExistingApplication | Out-Null
        return
    }

    try {
        if (-not (Test-Path $Python) -or -not (Test-Path $Caddy) -or -not (Test-Path $Caddyfile)) {
            throw "Faltan archivos de MS Contable o Caddy. Reinstalá la aplicación."
        }

        New-Item -ItemType Directory -Force -Path $DataDir, $LogsDir, $CaddyStorage | Out-Null
        $script:StartupLog = Join-Path $LogsDir "startup.log"
        $stageClock = [System.Diagnostics.Stopwatch]::StartNew()
        . (Join-Path $PSScriptRoot "protect-data.ps1")
        $aclWasRepaired = Protect-MSContableDataDirectory -Path $DataRoot
        $aclMessage = if ($aclWasRepaired) { "Permisos de datos protegidos o reparados" } else { "Permisos de datos verificados sin recorrido recursivo" }
        Write-StartupLog -Message ("{0} en {1} ms" -f $aclMessage, $stageClock.ElapsedMilliseconds)

        $sessionToken = ""
        if (Test-Path -LiteralPath $SessionTokenFile -PathType Leaf) {
            $sessionToken = (Get-Content -LiteralPath $SessionTokenFile -Raw).Trim()
        }
        if ($sessionToken -notmatch "^[0-9a-f]{32}$") {
            $sessionToken = [guid]::NewGuid().ToString("N")
            [System.IO.File]::WriteAllText($SessionTokenFile, $sessionToken, [System.Text.UTF8Encoding]::new($false))
        }
        $env:MSCONTABLE_SESSION_TOKEN = $sessionToken
        $env:MSCONTABLE_HEARTBEAT_DIR = $HeartbeatDir

        Start-BootstrapPage
        if (-not [string]::IsNullOrWhiteSpace($SplashSignalPath)) {
            try {
                [System.IO.File]::WriteAllText($SplashSignalPath, "opened")
            }
            catch {
                Write-StartupLog -Message ("No se pudo cerrar la pantalla breve de inicio: " + $_.Exception.Message)
            }
        }
        Set-StartupStage -Title "Preparando MS Contable" -Message "Verificando los componentes locales…"

        $env:MSCONTABLE_DATA_DIR = $DataDir
        $env:MSCONTABLE_LOG_DIR = $LogsDir
        $env:DJANGO_SETTINGS_MODULE = "ms_contable.settings_windows"
        $env:XDG_DATA_HOME = $CaddyDataHome
        $env:XDG_CONFIG_HOME = $DataRoot
        $waitressStdout = Join-Path $LogsDir "waitress.out.log"
        $waitressStderr = Join-Path $LogsDir "waitress.err.log"
        $caddyStdout = Join-Path $LogsDir "caddy.out.log"
        $caddyStderr = Join-Path $LogsDir "caddy.err.log"

        $BackendPort = Read-ConfiguredPort -Path $BackendPortFile -Default 0 -AllowedPorts $DynamicPorts
        $HttpsPort = Read-ConfiguredPort -Path $HttpsPortFile -Default 0 -AllowedPorts $DynamicPorts
        $waitressProcess = $null
        if (Test-Path $WaitressPidFile) {
            $processId = 0
            if ([int]::TryParse((Get-Content $WaitressPidFile -Raw), [ref]$processId)) {
                $waitressProcess = Get-ManagedProcess -ProcessId $processId -Executable $Python -CommandMarker "ms_contable.wsgi:application"
            }
        }
        $caddyProcess = $null
        if (Test-Path $CaddyPidFile) {
            $processId = 0
            if ([int]::TryParse((Get-Content $CaddyPidFile -Raw), [ref]$processId)) {
                $caddyProcess = Get-ManagedProcess -ProcessId $processId -Executable $Caddy -CommandMarker @($RuntimeCaddyfile, $Caddyfile)
            }
        }

        $servicesReady = $false
        if ($waitressProcess -and $caddyProcess -and $BackendPort -gt 0 -and $HttpsPort -gt 0) {
            $healthyClock = [System.Diagnostics.Stopwatch]::StartNew()
            $waitressReady = $false
            while (-not $waitressProcess.HasExited -and $healthyClock.Elapsed.TotalSeconds -lt 25) {
                try {
                    $response = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/admin/login/" -Headers @{ "X-Forwarded-Proto" = "https" } -UseBasicParsing -TimeoutSec 1
                    if ($response.StatusCode -eq 200) { $waitressReady = $true; break }
                }
                catch { Start-Sleep -Milliseconds 250 }
            }
            if ($waitressReady) {
                try {
                    Wait-ForCaddyCertificate -CaddyProcess $caddyProcess -Port $HttpsPort -TimeoutSeconds 5
                    $heartbeatResponse = Invoke-WebRequest `
                        -Uri "http://127.0.0.1:$BackendPort/_local/session-heartbeat/" `
                        -Method Post `
                        -Headers @{
                            "X-Forwarded-Proto" = "https"
                            "X-MSContable-Session" = $sessionToken
                            "X-MSContable-Tab" = "00000000000000000000000000000000"
                        } `
                        -UseBasicParsing `
                        -TimeoutSec 2
                    $servicesReady = $heartbeatResponse.StatusCode -eq 204
                    if ($servicesReady) {
                        try {
                            Invoke-WebRequest `
                                -Uri "http://127.0.0.1:$BackendPort/_local/session-heartbeat/" `
                                -Method Post `
                                -Headers @{
                                    "X-Forwarded-Proto" = "https"
                                    "X-MSContable-Session" = $sessionToken
                                    "X-MSContable-Tab" = "00000000000000000000000000000000"
                                    "X-MSContable-Closed" = "1"
                                } `
                                -UseBasicParsing `
                                -TimeoutSec 2 | Out-Null
                        }
                        catch {
                        }
                    }
                }
                catch {
                    Write-StartupLog -Message "La instancia activa no reconoció la sesión del navegador; se reiniciarán Waitress y Caddy"
                }
            }
        }

        if ($servicesReady) {
            Write-StartupLog -Message "Se reutilizan Waitress y Caddy en los puertos aleatorios $BackendPort y $HttpsPort"
        }
        else {
            Stop-ManagedProcess -PidFile $CaddyPidFile -Executable $Caddy -CommandMarker @($RuntimeCaddyfile, $Caddyfile)
            Stop-ManagedProcess -PidFile $WaitressPidFile -Executable $Python -CommandMarker "ms_contable.wsgi:application"
            Remove-Item -LiteralPath $HeartbeatDir -Force -Recurse -ErrorAction SilentlyContinue
            $sessionToken = [guid]::NewGuid().ToString("N")
            [System.IO.File]::WriteAllText($SessionTokenFile, $sessionToken, [System.Text.UTF8Encoding]::new($false))
            $env:MSCONTABLE_SESSION_TOKEN = $sessionToken

            $randomPorts = Get-RandomServicePorts
            $BackendPort = $randomPorts.BackendPort
            $HttpsPort = $randomPorts.HttpsPort
            $env:MSCONTABLE_HTTPS_PORT = [string]$HttpsPort
            Write-StartupLog -Message "Puertos aleatorios asignados: Waitress $BackendPort y HTTPS $HttpsPort"

            $waitressProcess = Start-WaitressOnRandomPort -Port $BackendPort
            Write-StartupLog -Message "Django respondió en el puerto aleatorio $BackendPort"
            $caddyProcess = Start-CaddyOnRandomPort -Port $HttpsPort
        }

        Set-StartupStage -Title "Asegurando la conexión" -Message "Esperando el certificado local de HTTPS…"
        $stageClock.Restart()
        Wait-ForCaddyCertificate -CaddyProcess $caddyProcess -Port $HttpsPort
        Write-StartupLog -Message ("Caddy presentó HTTPS en {0} ms" -f $stageClock.ElapsedMilliseconds)

        if (-not (Test-RootCertificateTrusted)) {
            Set-StartupStage -Title "Asegurando la conexión" -Message "Restaurando la confianza del certificado local…"
            Trust-ExistingRootCertificate
        }
        else {
            Write-StartupLog -Message "Certificado HTTPS ya confiable"
        }

        $stageClock.Restart()
        Wait-ForApplicationUrl -Port $HttpsPort
        Write-StartupLog -Message ("HTTPS y la página de acceso respondieron en {0} ms" -f $stageClock.ElapsedMilliseconds)
        Write-StartupLog -Message ("Inicio completo en {0} ms" -f $StartupClock.ElapsedMilliseconds)
        $loginUrl = "https://${SiteHost}:$HttpsPort/admin/login/"
        Write-StartupState -State "ready" -Title "MS Contable está listo" -Message "Abriendo la página de acceso…" -LoginUrl $loginUrl
        Signal-BrowserPageReady -HeartbeatDir $HeartbeatDir -SignalPath $SplashReadySignalPath
        Wait-ForBrowserSessionsToClose `
            -HeartbeatDir $HeartbeatDir `
            -WaitressPidFile $WaitressPidFile `
            -CaddyPidFile $CaddyPidFile `
            -Python $Python `
            -Caddy $Caddy `
            -RuntimeCaddyfile $RuntimeCaddyfile

        Stop-ManagedProcess -PidFile $BootstrapPidFile -Executable $Python -CommandMarker "bootstrap.py"
        Stop-ManagedProcess -PidFile $CaddyPidFile -Executable $Caddy -CommandMarker @($RuntimeCaddyfile, $Caddyfile)
        Stop-ManagedProcess -PidFile $WaitressPidFile -Executable $Python -CommandMarker "ms_contable.wsgi:application"
        Remove-Item -LiteralPath $BackendPortFile, $HttpsPortFile -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $HeartbeatDir -Force -Recurse -ErrorAction SilentlyContinue
    }
    catch {
        $errorMessage = $_.Exception.Message
        $errorDetails = "{0}`r`n`r`nRegistros de inicio: {1}" -f $_.Exception.ToString(), $StartupLog
        Write-StartupLog -Message ("Error de inicio: " + $_.Exception.ToString())
        $shortError = if ($errorMessage -match "(?i)Waitress|Django|puerto local") {
            "No se pudo iniciar el servidor local. Puede haber un conflicto de puertos o un problema al cargar los datos."
        }
        elseif ($errorMessage -match "(?i)Caddy|HTTPS|certificado") {
            "No se pudo preparar la conexión segura local."
        }
        else {
            "MS Contable no pudo completar el inicio."
        }
        $loginUrl = if ($HttpsPort -gt 0) { "https://${SiteHost}:$HttpsPort/admin/login/" } else { "" }
        Write-StartupState -State "error" -Title "No se pudo iniciar MS Contable" -Message "Consultá los detalles técnicos para obtener ayuda." -ErrorMessage $shortError -ErrorDetails $errorDetails -LoginUrl $loginUrl

        if ($startedCaddy -and -not $startedCaddy.HasExited) {
            Stop-Process -Id $startedCaddy.Id -Force -ErrorAction SilentlyContinue
            Remove-Item $CaddyPidFile -Force -ErrorAction SilentlyContinue
        }
        if ($startedWaitress -and -not $startedWaitress.HasExited) {
            Stop-Process -Id $startedWaitress.Id -Force -ErrorAction SilentlyContinue
            Remove-Item $WaitressPidFile -Force -ErrorAction SilentlyContinue
        }
        if (-not $browserOpened) {
            if ($bootstrapProcess -and -not $bootstrapProcess.HasExited) {
                Stop-Process -Id $bootstrapProcess.Id -Force -ErrorAction SilentlyContinue
            }
            Remove-Item -LiteralPath $BootstrapPidFile -Force -ErrorAction SilentlyContinue
            if ($StateFile) {
                Remove-Item -LiteralPath $StateFile -Force -ErrorAction SilentlyContinue
            }
            if ($PortFile) {
                Remove-Item -LiteralPath $PortFile -Force -ErrorAction SilentlyContinue
            }
            Show-StartupError -Message $errorMessage
        }
    }
}
finally {
    if ($ownsLauncherMutex) {
        $launcherMutex.ReleaseMutex()
    }
    $launcherMutex.Dispose()
}
