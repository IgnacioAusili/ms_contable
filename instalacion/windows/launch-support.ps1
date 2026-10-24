function Get-ManagedProcess {
    param(
        [int] $ProcessId,
        [string] $Executable,
        [string[]] $CommandMarker
    )

    $processInfo = Get-CimInstance Win32_Process -Filter "ProcessId = $ProcessId" -ErrorAction SilentlyContinue
    if (-not $processInfo -or -not [string]::Equals($processInfo.ExecutablePath, $Executable, [StringComparison]::OrdinalIgnoreCase)) {
        return $null
    }

    $hasCommandMarker = $false
    foreach ($marker in $CommandMarker) {
        if ($marker -and $processInfo.CommandLine -and
            $processInfo.CommandLine.IndexOf($marker, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
            $hasCommandMarker = $true
            break
        }
    }
    if (-not $hasCommandMarker) {
        return $null
    }

    return Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
}

function Stop-ManagedProcess {
    param(
        [string] $PidFile,
        [string] $Executable,
        [string[]] $CommandMarker
    )

    if (-not (Test-Path $PidFile)) {
        return
    }

    $processId = 0
    if ([int]::TryParse((Get-Content $PidFile -Raw), [ref]$processId)) {
        $process = Get-ManagedProcess -ProcessId $processId -Executable $Executable -CommandMarker $CommandMarker
        if ($process) {
            Stop-Process -Id $process.Id -Force
            $process.WaitForExit()
        }
    }

    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

function Read-ConfiguredPort {
    param(
        [string] $Path,
        [int] $Default,
        [int[]] $AllowedPorts
    )

    try {
        $value = 0
        $content = (Get-Content -LiteralPath $Path -Raw -ErrorAction Stop).Trim()
        if ([int]::TryParse($content, [ref]$value) -and $AllowedPorts -contains $value) {
            return $value
        }
    }
    catch {
    }

    return $Default
}

function Test-LocalPortAvailable {
    param([int] $Port)

    foreach ($address in @([System.Net.IPAddress]::Loopback, [System.Net.IPAddress]::IPv6Loopback)) {
        $listener = [System.Net.Sockets.TcpListener]::new($address, $Port)
        try {
            $listener.Start()
        }
        catch {
            return $false
        }
        finally {
            $listener.Stop()
        }
    }

    return $true
}

function Get-RandomLocalPort {
    param(
        [int[]] $ExcludePorts = @(),
        [int] $Attempts = 100
    )

    for ($attempt = 0; $attempt -lt $Attempts; $attempt++) {
        $port = Get-Random -Minimum 49152 -Maximum 65536
        if ($ExcludePorts -contains $port) {
            continue
        }
        if (Test-LocalPortAvailable -Port $port) {
            return $port
        }
    }

    throw "Windows no pudo asignar un puerto aleatorio libre para MS Contable."
}

function Get-RandomServicePorts {
    $backendPort = Get-RandomLocalPort
    $httpsPort = Get-RandomLocalPort -ExcludePorts @($backendPort)
    return [pscustomobject]@{
        BackendPort = $backendPort
        HttpsPort = $httpsPort
    }
}

function Write-RuntimeCaddyfile {
    param(
        [string] $Path,
        [int] $HttpsPort,
        [int] $BackendPort
    )

    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Path) | Out-Null
    $configuration = @"
{
    admin off
    auto_https disable_redirects
    skip_install_trust
}

https://mscontable:$HttpsPort {
    bind 127.0.0.1 ::1
    tls internal
    reverse_proxy 127.0.0.1:$BackendPort
}
"@
    [System.IO.File]::WriteAllText($Path, $configuration, [System.Text.UTF8Encoding]::new($false))
}

function Write-StartupLog {
    param([string] $Message)

    if (-not (Test-Path $LogsDir -PathType Container)) {
        return
    }

    if ((Test-Path $StartupLog -PathType Leaf) -and (Get-Item $StartupLog).Length -gt 1048576) {
        Move-Item -LiteralPath $StartupLog -Destination "$StartupLog.1" -Force
    }

    $line = "{0} +{1}ms {2}{3}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"), $StartupClock.ElapsedMilliseconds, $Message, [Environment]::NewLine
    [System.IO.File]::AppendAllText($StartupLog, $line, [System.Text.UTF8Encoding]::new($false))
}

function Write-StartupState {
    param(
        [string] $State,
        [string] $Title,
        [string] $Message,
        [string] $ErrorMessage = "",
        [string] $ErrorDetails = "",
        [string] $LoginUrl = ""
    )

    if (-not $StateFile) {
        return
    }

    $stateContent = @{
        state = $State
        title = $Title
        message = $Message
        error = $ErrorMessage
        details = $ErrorDetails
        login_url = $LoginUrl
    } | ConvertTo-Json -Compress
    $temporaryFile = "$StateFile.$PID.tmp"
    [System.IO.File]::WriteAllText($temporaryFile, $stateContent, [System.Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $temporaryFile -Destination $StateFile -Force
}

function Set-StartupStage {
    param(
        [string] $Title,
        [string] $Message
    )

    Write-StartupState -State "starting" -Title $Title -Message $Message
    Write-StartupLog -Message ("Etapa: " + $Title)
}

function Start-BootstrapPage {
    if (-not (Test-Path $BootstrapScript -PathType Leaf)) {
        throw "No se encontró la página de inicio de MS Contable. Reinstalá la aplicación."
    }

    Stop-ManagedProcess -PidFile $BootstrapPidFile -Executable $Python -CommandMarker "bootstrap.py"

    $instanceId = [guid]::NewGuid().ToString("N")
    $script:StateFile = Join-Path $DataDir "startup-$instanceId.json"
    $script:PortFile = Join-Path $DataDir "startup-$instanceId.port"
    $openedFile = Join-Path $DataDir "startup-$instanceId.opened"
    $bootstrapLog = Join-Path $LogsDir "bootstrap.log"
    $bootstrapErrorLog = Join-Path $LogsDir "bootstrap.err.log"
    Write-StartupState -State "starting" -Title "Preparando el programa" -Message "La aplicación se abrirá en unos instantes."

    $arguments = "`"$BootstrapScript`" --state-file `"$StateFile`" --port-file `"$PortFile`" --opened-file `"$openedFile`""
    $script:bootstrapProcess = Start-Process `
        -FilePath $Python `
        -ArgumentList $arguments `
        -WorkingDirectory $InstallDir `
        -WindowStyle Hidden `
        -PassThru `
        -RedirectStandardOutput $bootstrapLog `
        -RedirectStandardError $bootstrapErrorLog
    Set-Content -LiteralPath $BootstrapPidFile -Value $bootstrapProcess.Id -Encoding ASCII

    $port = 0
    for ($attempt = 0; $attempt -lt 100; $attempt++) {
        if ($bootstrapProcess.HasExited) {
            $detailLines = @($bootstrapLog, $bootstrapErrorLog) |
                Where-Object { Test-Path $_ -PathType Leaf } |
                ForEach-Object { (Get-Content $_ -Raw).Trim() } |
                Where-Object { $_ }
            $details = $detailLines -join " "
            throw "No se pudo preparar la pantalla de inicio local. $details"
        }
        if (Test-Path $PortFile -PathType Leaf) {
            $portText = (Get-Content -LiteralPath $PortFile -Raw).Trim()
            if ([int]::TryParse($portText, [ref]$port) -and $port -gt 0 -and $port -le 65535) {
                break
            }
        }
        Start-Sleep -Milliseconds 50
    }

    if ($port -eq 0) {
        throw "La pantalla de inicio local no respondió a tiempo. Revisá los registros en $LogsDir."
    }

    Start-Process ("http://127.0.0.1:{0}/" -f $port)
    $script:browserOpened = $true
    Write-StartupLog -Message ("Pantalla de carga abierta en el puerto local {0}" -f $port)

    $pageClock = [System.Diagnostics.Stopwatch]::StartNew()
    while (-not (Test-Path -LiteralPath $openedFile -PathType Leaf) -and $pageClock.Elapsed.TotalSeconds -lt 12) {
        if ($script:bootstrapProcess.HasExited) {
            break
        }
        Start-Sleep -Milliseconds 100
    }
    if (Test-Path -LiteralPath $openedFile -PathType Leaf) {
        Write-StartupLog -Message ("El navegador cargó la página inicial en {0} ms" -f $pageClock.ElapsedMilliseconds)
    }
}

function Test-RootCertificateTrusted {
    if (-not (Test-Path $RootCertificate)) {
        return $false
    }

    $certificate = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($RootCertificate)
    $store = [System.Security.Cryptography.X509Certificates.X509Store]::new("Root", "CurrentUser")
    $store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadOnly)
    try {
        return $store.Certificates.Find(
            [System.Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint,
            $certificate.Thumbprint,
            $false
        ).Count -gt 0
    }
    finally {
        $store.Close()
    }
}

function Trust-ExistingRootCertificate {
    $preparationScript = Join-Path $PSScriptRoot "prepare-https.ps1"
    if (-not (Test-Path $preparationScript)) {
        throw "No se encontró la rutina para reparar HTTPS de MS Contable. Reinstalá la aplicación."
    }

    $repairLog = Join-Path $LogsDir "https-repair.log"
    $powerShell = Join-Path $PSHOME "powershell.exe"
    & $powerShell -NoProfile -STA -ExecutionPolicy Bypass -WindowStyle Hidden -File $preparationScript -NoUI -TrustExistingCertificateOnly *> $repairLog
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo confiar en el certificado HTTPS local. Revisá los registros en $LogsDir."
    }

    if (-not (Test-RootCertificateTrusted)) {
        throw "Windows no confirmó la confianza del certificado HTTPS de MS Contable. Revisá los registros en $LogsDir."
    }
}

function Wait-ForCaddyCertificate {
    param(
        [System.Diagnostics.Process] $CaddyProcess,
        [int] $Port,
        [int] $TimeoutSeconds = 20
    )

    $timeoutClock = [System.Diagnostics.Stopwatch]::StartNew()
    $callback = [System.Net.Security.RemoteCertificateValidationCallback] {
        param($sender, $certificate, $chain, $errors)
        return $true
    }

    for ($attempt = 0; $attempt -lt 120; $attempt++) {
        if ($timeoutClock.Elapsed.TotalSeconds -ge $TimeoutSeconds) {
            break
        }
        if ($CaddyProcess.HasExited) {
            throw "Caddy se cerró al iniciar. Revisá los logs en $LogsDir."
        }

        $client = [System.Net.Sockets.TcpClient]::new()
        $client.ReceiveTimeout = 1000
        $client.SendTimeout = 1000
        $stream = $null
        try {
            $client.Connect([System.Net.IPAddress]::Loopback, $Port)
            $stream = [System.Net.Security.SslStream]::new($client.GetStream(), $false, $callback)
            $stream.AuthenticateAsClient($SiteHost)
            $certificate = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($stream.RemoteCertificate)
            if ($certificate.GetNameInfo([System.Security.Cryptography.X509Certificates.X509NameType]::DnsName, $false) -ne $SiteHost) {
                throw "Caddy presentó un certificado para otro nombre."
            }
            if (Test-Path $RootCertificate) {
                return
            }
        }
        catch {
            Start-Sleep -Milliseconds 250
        }
        finally {
            if ($stream) {
                $stream.Dispose()
            }
            $client.Dispose()
        }
    }

    throw "Caddy no pudo emitir el certificado local. Revisá los logs en $LogsDir."
}

function Wait-ForApplicationUrl {
    param([int] $Port)

    $loginUrl = if ($Port -eq 443) { "https://${SiteHost}/admin/login/" } else { "https://${SiteHost}:$Port/admin/login/" }
    $timeoutClock = [System.Diagnostics.Stopwatch]::StartNew()
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        if ($timeoutClock.Elapsed.TotalSeconds -ge 20) {
            break
        }
        try {
            $response = Invoke-WebRequest `
                -Uri $loginUrl `
                -UseBasicParsing `
                -TimeoutSec 1
            if ($response.StatusCode -eq 200) {
                return
            }
        }
        catch {
            Start-Sleep -Milliseconds 250
        }
    }

    throw "La página de acceso HTTPS no respondió. Revisá los registros en $LogsDir."
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
