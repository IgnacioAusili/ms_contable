param(
    [string] $PythonCommand = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ToolsRoot = Join-Path $PSScriptRoot ".tools"
if ([string]::IsNullOrWhiteSpace($PythonCommand)) {
    $localPython = Get-ChildItem $ToolsRoot -Directory -Filter "python-*" -ErrorAction SilentlyContinue |
        Where-Object { Test-Path (Join-Path $_.FullName "python.exe") } |
        Sort-Object { [version]($_.Name -replace '^python-', '') } -Descending |
        ForEach-Object { Join-Path $_.FullName "python.exe" } |
        Select-Object -First 1
    $PythonCommand = if ($localPython) { $localPython } else { "python" }
}

$Python = (Get-Command $PythonCommand -ErrorAction Stop).Source
$versionText = & $Python -c "import platform; print(platform.python_version())"
$architecture = & $Python -c "import platform; print(platform.architecture()[0])"
$implementation = & $Python -c "import platform; print(platform.python_implementation())"
$pythonVersion = [version]$versionText

if ($implementation -ne "CPython" -or $pythonVersion -lt [version]"3.11.9" -or $pythonVersion.Major -ne 3 -or $pythonVersion.Minor -gt 13) {
    throw "El proceso de construcción requiere CPython 3.11.9 a 3.13 x64. Detectado: $implementation $versionText."
}

if ($architecture -ne "64bit") {
    throw "El instalador requiere CPython x64. Detectado: $architecture."
}

$BuildRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "build"))
$InstallerRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
if (-not $BuildRoot.StartsWith("$InstallerRoot\", [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "La ruta temporal de construcción está fuera de instalacion\windows."
}

if (Test-Path $BuildRoot) {
    Remove-Item $BuildRoot -Recurse -Force
}

$Payload = Join-Path $BuildRoot "payload"
$AppPayload = Join-Path $Payload "app"
$Runtime = Join-Path $Payload "python"
$SitePackages = Join-Path $Runtime "Lib\site-packages"
$PythonZip = Join-Path $BuildRoot "python-embed.zip"
New-Item -ItemType Directory -Force -Path $Payload, $SitePackages | Out-Null

$pythonVersionForUrl = $pythonVersion.ToString(3)
$runtimeUrl = "https://www.python.org/ftp/python/$pythonVersionForUrl/python-$pythonVersionForUrl-embed-amd64.zip"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -UseBasicParsing -Uri $runtimeUrl -OutFile $PythonZip
Expand-Archive -LiteralPath $PythonZip -DestinationPath $Runtime

$pythonTag = "python$($pythonVersion.Major)$($pythonVersion.Minor)"
$pythonPathFile = Join-Path $Runtime "$pythonTag._pth"
if (-not (Test-Path $pythonPathFile)) {
    throw "El paquete embebible descargado no contiene $pythonTag._pth."
}

Set-Content -Path $pythonPathFile -Encoding ASCII -Value @(
    "$pythonTag.zip",
    ".",
    "..\app",
    "..",
    "Lib\site-packages",
    "import site"
)

& $Python -m pip install --disable-pip-version-check --no-compile --target $SitePackages -r (Join-Path $ProjectRoot "requirements-windows.txt")
if ($LASTEXITCODE -ne 0) {
    throw "No se pudieron preparar las dependencias de Windows."
}

$excludedRoots = @(
    ".git", ".github", ".venv", "venv", "env", "data", "logs", "staticfiles", "docs",
    "instalacion", "node_modules", ".playwright-cli", ".ruff_cache", ".pytest_cache",
    "tmp", ".idea", ".vscode"
)
$trackedFiles = & git -C $ProjectRoot ls-files --cached --others --exclude-standard
if ($LASTEXITCODE -ne 0) {
    throw "No se pudo obtener la lista de archivos del repositorio."
}

foreach ($relativePath in $trackedFiles) {
    $normalizedPath = $relativePath.Replace("/", "\")
    $rootName = $normalizedPath.Split("\")[0]
    $fileName = [System.IO.Path]::GetFileName($normalizedPath)

    if ($excludedRoots -contains $rootName -or $fileName -match '^(\.env(\..*)?|local_settings\.py)$') {
        continue
    }

    if ($normalizedPath -match '(?i)(^|\\)tests?(\\|$)|(^|\\)test[^\\]*\.py$' -or $fileName -match '(?i)\.(pyc|pyo|sqlite3.*|db|bak|log|pdf)$') {
        continue
    }

    $sourceFile = Join-Path $ProjectRoot $normalizedPath
    if (-not (Test-Path $sourceFile -PathType Leaf)) {
        continue
    }

    $destinationFile = Join-Path $AppPayload $normalizedPath
    $destinationDirectory = Split-Path -Parent $destinationFile
    New-Item -ItemType Directory -Force -Path $destinationDirectory | Out-Null
    Copy-Item -LiteralPath $sourceFile -Destination $destinationFile
}

$AppWindows = Join-Path $AppPayload "windows"
New-Item -ItemType Directory -Force -Path $AppWindows | Out-Null
Copy-Item (Join-Path $PSScriptRoot "launch.ps1") $AppWindows
Copy-Item (Join-Path $PSScriptRoot "launch-hidden.vbs") $AppWindows
Copy-Item (Join-Path $PSScriptRoot "initialize.ps1") $AppWindows

$env:MSCONTABLE_DATA_DIR = Join-Path $BuildRoot "data"
$env:MSCONTABLE_LOG_DIR = Join-Path $BuildRoot "logs"
New-Item -ItemType Directory -Force -Path $env:MSCONTABLE_DATA_DIR, $env:MSCONTABLE_LOG_DIR | Out-Null
Push-Location $AppPayload
try {
    & (Join-Path $Runtime "python.exe") manage.py collectstatic --noinput
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudieron preparar los archivos estáticos."
    }
}
finally {
    Pop-Location
    Remove-Item Env:MSCONTABLE_DATA_DIR, Env:MSCONTABLE_LOG_DIR -ErrorAction SilentlyContinue
}

$versionLine = Get-Content (Join-Path $ProjectRoot "ms_contable\settings.py") |
    Where-Object { $_ -match '^APP_VERSION\s*=' } |
    Select-Object -First 1
if (-not $versionLine -or $versionLine -notmatch '"([^"]+)"') {
    throw "No se pudo leer APP_VERSION desde ms_contable\settings.py."
}
$appVersion = $Matches[1]

$isccCommand = Get-Command ISCC.exe -ErrorAction SilentlyContinue
$isccCandidates = @(
    (Join-Path $PSScriptRoot ".tools\innosetup-7.1.0\ISCC.exe"),
    (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 7\ISCC.exe"),
    (Join-Path $env:ProgramFiles "Inno Setup 7\ISCC.exe"),
    (Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"),
    (Join-Path $env:ProgramFiles "Inno Setup 6\ISCC.exe")
)
$iscc = if ($isccCommand) { $isccCommand.Source } else { $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1 }
if (-not $iscc) {
    throw "El contenido quedó preparado en $Payload. Instalá Inno Setup 6 o 7 y volvé a ejecutar este script para generar el instalador."
}

New-Item -ItemType Directory -Force -Path (Join-Path $PSScriptRoot "dist") | Out-Null
Set-Location $PSScriptRoot
& $iscc "/DAppVersion=$appVersion" "setup.iss"
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup no pudo compilar el instalador."
}

Write-Host "Instalador generado en $(Join-Path $PSScriptRoot "dist\MSContable-Setup-$appVersion.exe")"
