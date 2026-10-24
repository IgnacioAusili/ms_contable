$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
$NoUI = $args -contains "-NoUI"
$TrustExistingCertificateOnly = $args -contains "-TrustExistingCertificateOnly"

$InstallDir = Split-Path -Parent $PSScriptRoot
$DataRoot = Join-Path $env:LOCALAPPDATA "MSContable"
$DataDir = Join-Path $DataRoot "data"
$LogsDir = Join-Path $DataRoot "logs"
$Caddy = Join-Path $InstallDir "caddy\caddy.exe"
$Caddyfile = Join-Path $InstallDir "caddy\Caddyfile"
$RuntimeCaddyfile = Join-Path $DataRoot "config\runtime.Caddyfile"
$CaddyStorage = Join-Path $DataRoot "caddy"
$RootCertificate = Join-Path $CaddyStorage "pki\authorities\local\root.crt"
$ThumbprintFile = Join-Path $DataDir "caddy-ca-thumbprint.txt"
$BackendPort = 8000
$HttpsPort = 0
$SiteHost = "mscontable"
$CaddyProcess = $null
$StartupClock = [System.Diagnostics.Stopwatch]::StartNew()
$StartupLog = Join-Path $LogsDir "startup.log"

. (Join-Path $PSScriptRoot "launch-support.ps1")

function Show-Message {
    param(
        [string] $Message,
        [string] $Title,
        [System.Windows.Forms.MessageBoxButtons] $Buttons,
        [System.Windows.Forms.MessageBoxIcon] $Icon
    )

    return [System.Windows.Forms.MessageBox]::Show($Message, $Title, $Buttons, $Icon)
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

function Add-RootCertificateToCurrentUser {
    $certificate = [System.Security.Cryptography.X509Certificates.X509Certificate2]::new($RootCertificate)
    if (-not $certificate.Subject.StartsWith(
        "CN=Caddy Local Authority",
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw "El certificado HTTPS local no pertenece a la autoridad de Caddy esperada."
    }

    $previousThumbprint = ""
    if (Test-Path $ThumbprintFile) {
        $previousThumbprint = (Get-Content $ThumbprintFile -Raw).Trim()
    }

    $store = [System.Security.Cryptography.X509Certificates.X509Store]::new("Root", "CurrentUser")
    $store.Open([System.Security.Cryptography.X509Certificates.OpenFlags]::ReadWrite)
    try {
        $current = $store.Certificates.Find(
            [System.Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint,
            $certificate.Thumbprint,
            $false
        )
        if ($current.Count -eq 0) {
            $store.Add($certificate)
        }

        $current = $store.Certificates.Find(
            [System.Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint,
            $certificate.Thumbprint,
            $false
        )
        if ($current.Count -eq 0) {
            throw "Windows no pudo confiar en el certificado HTTPS local de MS Contable."
        }

        if ($previousThumbprint -and $previousThumbprint -ne $certificate.Thumbprint) {
            $previous = $store.Certificates.Find(
                [System.Security.Cryptography.X509Certificates.X509FindType]::FindByThumbprint,
                $previousThumbprint,
                $false
            )
            foreach ($oldCertificate in $previous) {
                if ($oldCertificate.Subject.StartsWith(
                    "CN=Caddy Local Authority",
                    [System.StringComparison]::OrdinalIgnoreCase
                )) {
                    $store.Remove($oldCertificate)
                }
            }
        }
    }
    finally {
        $store.Close()
    }

    Set-Content -Path $ThumbprintFile -Value $certificate.Thumbprint -Encoding ASCII
}

try {
    New-Item -ItemType Directory -Force -Path $DataDir, $LogsDir, $CaddyStorage, (Split-Path -Parent $RuntimeCaddyfile) | Out-Null
    $env:XDG_DATA_HOME = $DataRoot
    $env:XDG_CONFIG_HOME = $DataRoot

    if (Test-RootCertificateTrusted) {
        Add-RootCertificateToCurrentUser
        exit 0
    }

    if ($TrustExistingCertificateOnly) {
        if (-not (Test-Path $RootCertificate -PathType Leaf)) {
            throw "Caddy todavía no generó el certificado HTTPS local de MS Contable."
        }

        Add-RootCertificateToCurrentUser
        exit 0
    }

    if (-not (Test-Path $Caddy) -or -not (Test-Path $Caddyfile)) {
        throw "No se encontraron los archivos de Caddy incluidos con MS Contable."
    }

    $caddyStdout = Join-Path $LogsDir "caddy-install.out.log"
    $caddyStderr = Join-Path $LogsDir "caddy-install.err.log"
    $HttpsPort = Get-RandomLocalPort
    Write-RuntimeCaddyfile -Path $RuntimeCaddyfile -HttpsPort $HttpsPort -BackendPort $BackendPort
    $CaddyProcess = Start-Process `
        -FilePath $Caddy `
        -ArgumentList @("run", "--config", "`"$RuntimeCaddyfile`"", "--adapter", "caddyfile") `
        -WorkingDirectory (Split-Path -Parent $Caddy) `
        -WindowStyle Hidden `
        -PassThru `
        -RedirectStandardOutput $caddyStdout `
        -RedirectStandardError $caddyStderr

    Wait-ForCaddyCertificate -CaddyProcess $CaddyProcess -Port $HttpsPort -TimeoutSeconds 15
    Add-RootCertificateToCurrentUser
    Set-Content -Path (Join-Path $DataDir "caddy.port") -Value $HttpsPort -Encoding ASCII
    Write-StartupLog -Message "Certificado local preparado en el puerto HTTPS aleatorio $HttpsPort"
}
catch {
    if (-not $NoUI) {
        Show-Message `
            -Message $_.Exception.Message `
            -Title "No se pudo configurar HTTPS" `
            -Buttons ([System.Windows.Forms.MessageBoxButtons]::OK) `
            -Icon ([System.Windows.Forms.MessageBoxIcon]::Error) | Out-Null
    }
    exit 1
}
finally {
    if ($CaddyProcess -and -not $CaddyProcess.HasExited) {
        Stop-Process -Id $CaddyProcess.Id -Force -ErrorAction SilentlyContinue
        $CaddyProcess.WaitForExit()
    }
}
