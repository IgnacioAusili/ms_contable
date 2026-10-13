$ErrorActionPreference = "Stop"
$AppDir = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $AppDir "python\python.exe"
$DataDir = Join-Path $env:LOCALAPPDATA "MSContable\data"
$LogsDir = Join-Path $env:LOCALAPPDATA "MSContable\logs"
$Database = Join-Path $DataDir "db.sqlite3"
$Backup1 = Join-Path $DataDir "db.sqlite3.1.bak"
$Backup2 = Join-Path $DataDir "db.sqlite3.2.bak"
$Launcher = Join-Path $PSScriptRoot "launch.ps1"

New-Item -ItemType Directory -Force -Path $DataDir, $LogsDir | Out-Null
& powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $Launcher -Action Stop
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo detener MS Contable antes de inicializar o actualizar."
}

$env:MSCONTABLE_DATA_DIR = $DataDir
$env:MSCONTABLE_LOG_DIR = $LogsDir
Push-Location $AppDir

try {
    if (-not (Test-Path $Database)) {
        $legacyDatabase = Read-Host "Base SQLite anterior (ruta a db.sqlite3; Enter para una instalación nueva)"
        $legacyDatabase = $legacyDatabase.Trim().Trim('"')

        if ($legacyDatabase) {
            if (-not (Test-Path $legacyDatabase -PathType Leaf)) {
                throw "No existe la base indicada: $legacyDatabase"
            }

            Copy-Item $legacyDatabase $Database
            foreach ($suffix in @(".1.bak", ".2.bak")) {
                $legacyBackup = "$legacyDatabase$suffix"
                if (Test-Path $legacyBackup) {
                    Copy-Item $legacyBackup ("$Database$suffix") -Force
                }
            }
        }
    }

    if (Test-Path $Database) {
        if (Test-Path $Backup1) {
            if (Test-Path $Backup2) {
                Remove-Item $Backup2 -Force
            }
            Move-Item $Backup1 $Backup2 -Force
        }

        Copy-Item $Database $Backup1 -Force
    }

    & $Python manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudieron aplicar las migraciones. El respaldo anterior sigue disponible en $Backup1."
    }

    $probe = "from django.contrib.auth import get_user_model; print(get_user_model().objects.filter(is_superuser=True).exists())"
    $hasSuperuser = & $Python manage.py shell -c $probe
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo comprobar el usuario administrador."
    }

    $superuserExists = $hasSuperuser | ForEach-Object { $_.Trim() } | Where-Object { $_ -in @("True", "False") } | Select-Object -Last 1
    if ($superuserExists -ne "True") {
        $username = Read-Host "Usuario administrador"
        if ([string]::IsNullOrWhiteSpace($username)) {
            throw "El usuario no puede estar vacío. Ejecutá nuevamente la inicialización para reintentar."
        }

        $password = Read-Host "Contraseña" -AsSecureString
        $confirmation = Read-Host "Confirmar contraseña" -AsSecureString
        $passwordText = [System.Net.NetworkCredential]::new("", $password).Password
        $confirmationText = [System.Net.NetworkCredential]::new("", $confirmation).Password

        if ([string]::IsNullOrEmpty($passwordText) -or $passwordText -ne $confirmationText) {
            throw "Las contraseñas están vacías o no coinciden. Ejecutá nuevamente la inicialización para reintentar."
        }

        $env:DJANGO_SUPERUSER_USERNAME = $username
        $env:DJANGO_SUPERUSER_PASSWORD = $passwordText
        $env:DJANGO_SUPERUSER_EMAIL = ""
        & $Python manage.py createsuperuser --noinput
        $createStatus = $LASTEXITCODE
        Remove-Item Env:DJANGO_SUPERUSER_USERNAME, Env:DJANGO_SUPERUSER_PASSWORD, Env:DJANGO_SUPERUSER_EMAIL -ErrorAction SilentlyContinue

        if ($createStatus -ne 0) {
            throw "No se pudo crear el usuario administrador. Ejecutá nuevamente la inicialización para reintentar."
        }
    }

    Write-Host "MS Contable quedó inicializado. Se abrirá en el navegador."
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $Launcher -Action Start
}
finally {
    Pop-Location
    Remove-Item Env:MSCONTABLE_DATA_DIR, Env:MSCONTABLE_LOG_DIR -ErrorAction SilentlyContinue
}
