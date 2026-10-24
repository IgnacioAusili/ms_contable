param(
    [ValidateSet("", "preserve", "delete")]
    [string] $IncompatibleDataAction = ""
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Windows.Forms

$InstallDir = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $InstallDir "python\python.exe"
$AppDir = $InstallDir
$DataRoot = Join-Path $env:LOCALAPPDATA "MSContable"
$DataDir = Join-Path $env:LOCALAPPDATA "MSContable\data"
$LogsDir = Join-Path $env:LOCALAPPDATA "MSContable\logs"
$Database = Join-Path $DataDir "db.sqlite3"
$Backup1 = Join-Path $DataDir "db.sqlite3.1.bak"
$Backup2 = Join-Path $DataDir "db.sqlite3.2.bak"
$Launcher = Join-Path $PSScriptRoot "launch.ps1"
$PowerShell = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
$SetupLog = Join-Path $LogsDir "initialize.log"

function Show-Message {
    param(
        [string] $Message,
        [string] $Title,
        [System.Windows.Forms.MessageBoxButtons] $Buttons,
        [System.Windows.Forms.MessageBoxIcon] $Icon
    )

    return [System.Windows.Forms.MessageBox]::Show($Message, $Title, $Buttons, $Icon)
}

function Select-LegacyDatabase {
    $answer = Show-Message `
        -Message "¿Querés importar una base SQLite existente? Elegí No para crear una base nueva." `
        -Title "Base de datos de MS Contable" `
        -Buttons ([System.Windows.Forms.MessageBoxButtons]::YesNo) `
        -Icon ([System.Windows.Forms.MessageBoxIcon]::Question)

    if ($answer -ne [System.Windows.Forms.DialogResult]::Yes) {
        return
    }

    $dialog = [System.Windows.Forms.OpenFileDialog]::new()
    $dialog.Title = "Seleccionar base SQLite"
    $dialog.Filter = "Bases SQLite (*.sqlite3;*.db)|*.sqlite3;*.db|Todos los archivos (*.*)|*.*"
    $dialog.CheckFileExists = $true
    $dialog.Multiselect = $false
    if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        Copy-Item $dialog.FileName $Database
        foreach ($suffix in @(".1.bak", ".2.bak")) {
            $legacyBackup = "$($dialog.FileName)$suffix"
            if (Test-Path $legacyBackup) {
                Copy-Item $legacyBackup ("$Database$suffix") -Force
            }
        }
    }
    $dialog.Dispose()
}

function Invoke-ManageCommand {
    param(
        [string[]] $Arguments,
        [string] $Operation
    )

    $name = ($Operation -replace "[^A-Za-z0-9]+", "-").Trim("-").ToLowerInvariant()
    $stdout = Join-Path $LogsDir "$name.out.log"
    $stderr = Join-Path $LogsDir "$name.err.log"
    $process = Start-Process `
        -FilePath $Python `
        -ArgumentList $Arguments `
        -WorkingDirectory $AppDir `
        -WindowStyle Hidden `
        -PassThru `
        -Wait `
        -RedirectStandardOutput $stdout `
        -RedirectStandardError $stderr

    if ($process.ExitCode -ne 0) {
        throw "$Operation falló. Revisá los registros en $LogsDir."
    }
}

function Resolve-IncompatibleDatabase {
    if (-not $IncompatibleDataAction) {
        return
    }

    $databaseKey = Join-Path $DataRoot "config\database-key.dpapi"
    if ($IncompatibleDataAction -eq "preserve") {
        $archiveRoot = Join-Path $DataRoot "datos-anteriores"
        $archiveName = "sqlcipher-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        $archivePath = Join-Path $archiveRoot $archiveName
        $suffix = 1
        while (Test-Path -LiteralPath $archivePath) {
            $archivePath = Join-Path $archiveRoot "$archiveName-$suffix"
            $suffix++
        }

        New-Item -ItemType Directory -Force -Path $archiveRoot | Out-Null
        New-Item -ItemType Directory -Force -Path $archivePath | Out-Null
        if (Test-Path -LiteralPath $DataDir) {
            Move-Item -LiteralPath $DataDir -Destination (Join-Path $archivePath "data")
        }
        if (Test-Path -LiteralPath $databaseKey) {
            $archiveConfig = Join-Path $archivePath "config"
            New-Item -ItemType Directory -Force -Path $archiveConfig | Out-Null
            Move-Item -LiteralPath $databaseKey -Destination $archiveConfig
        }
        New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
        Add-Content -Path $SetupLog -Value "$(Get-Date -Format o) Se conservaron los datos cifrados en $archivePath."
        return
    }

    if (Test-Path -LiteralPath $DataDir) {
        Remove-Item -LiteralPath $DataDir -Recurse -Force
    }
    if (Test-Path -LiteralPath $databaseKey) {
        Remove-Item -LiteralPath $databaseKey -Force
    }
    New-Item -ItemType Directory -Force -Path $DataDir | Out-Null
    Add-Content -Path $SetupLog -Value "$(Get-Date -Format o) Se eliminaron los datos cifrados incompatibles por elección del usuario."
}

try {
    if (-not (Test-Path $Python) -or -not (Test-Path (Join-Path $AppDir "manage.py"))) {
        throw "Faltan archivos de MS Contable. Volvé a ejecutar el instalador."
    }

    New-Item -ItemType Directory -Force -Path $DataDir, $LogsDir | Out-Null
    . (Join-Path $PSScriptRoot "protect-data.ps1")
    Protect-MSContableDataDirectory -Path $DataRoot | Out-Null

    $env:MSCONTABLE_DATA_DIR = $DataDir
    $env:MSCONTABLE_LOG_DIR = $LogsDir
    $env:DJANGO_SETTINGS_MODULE = "ms_contable.settings_windows"

    & $PowerShell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $Launcher -Action Stop
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudieron detener los servicios anteriores de MS Contable."
    }

    Resolve-IncompatibleDatabase

    if (-not (Test-Path $Database) -and -not $IncompatibleDataAction) {
        Select-LegacyDatabase
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

    Invoke-ManageCommand -Arguments @("manage.py", "migrate", "--noinput") -Operation "Aplicar migraciones"
}
catch {
    New-Item -ItemType Directory -Force -Path $LogsDir | Out-Null
    $errorDetails = "$(Get-Date -Format o)`r`n$($_.Exception.ToString())"
    try {
        [System.IO.File]::WriteAllText(
            (Join-Path $LogsDir "initialize-failure.log"),
            $errorDetails,
            [System.Text.UTF8Encoding]::new($false)
        )
    }
    catch {
    }
    try {
        Add-Content -Path $SetupLog -Value $errorDetails
    }
    catch {
    }
    exit 1
}
finally {
    Remove-Item Env:MSCONTABLE_DATA_DIR, Env:MSCONTABLE_LOG_DIR, Env:DJANGO_SETTINGS_MODULE -ErrorAction SilentlyContinue
}
