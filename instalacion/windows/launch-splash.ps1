$ErrorActionPreference = "Stop"
$launcherLog = Join-Path $env:LOCALAPPDATA "MSContable\logs\launcher.log"

trap {
    $failure = $_.Exception.ToString()
    try { Restore-SystemCursor } catch {}
    try {
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $launcherLog) | Out-Null
        Add-Content -LiteralPath $launcherLog -Value ("{0} {1}{2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"), $failure, [Environment]::NewLine)
    }
    catch {
    }
    try {
        if ([System.Windows.Forms.MessageBox]) {
            [System.Windows.Forms.MessageBox]::Show(
                "No se pudo iniciar MS Contable. Consultá el registro en:`r`n$launcherLog`r`n`r`n$($_.Exception.Message)",
                "MS Contable",
                [System.Windows.Forms.MessageBoxButtons]::OK,
                [System.Windows.Forms.MessageBoxIcon]::Error
            ) | Out-Null
        }
    }
    catch {
    }
    try {
        if ($script:entryMutexOwned) { $script:entryMutex.ReleaseMutex() }
        if ($script:entryMutex) { $script:entryMutex.Dispose() }
    }
    catch {
    }
    exit 1
}

$script:entryMutex = [System.Threading.Mutex]::new($false, "Local\MSContableLauncherEntry")
$script:entryMutexOwned = $false
try {
    $script:entryMutexOwned = $script:entryMutex.WaitOne(0)
}
catch [System.Threading.AbandonedMutexException] {
    $script:entryMutexOwned = $true
}

if (-not $script:entryMutexOwned) {
    $script:entryMutex.Dispose()
    exit 0
}

$activeLauncherMutex = $null
try {
    $activeLauncherMutex = [System.Threading.Mutex]::OpenExisting("Local\MSContableLauncher")
}
catch {
}

if ($activeLauncherMutex) {
    try {
        $launchScript = Join-Path $PSScriptRoot "launch.ps1"
        $powerShell = Join-Path $PSHOME "powershell.exe"
        $arguments = "-NoProfile -STA -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$launchScript`" -Action Start"
        Start-Process -FilePath $powerShell -ArgumentList $arguments -WindowStyle Hidden -Wait | Out-Null
    }
    finally {
        $activeLauncherMutex.Dispose()
        $script:entryMutex.ReleaseMutex()
        $script:entryMutex.Dispose()
    }
    exit 0
}

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class MSContableCursorNative {
    [DllImport("user32.dll", SetLastError = true)] public static extern IntPtr LoadCursor(IntPtr instance, IntPtr cursorName);
    [DllImport("user32.dll", SetLastError = true)] public static extern IntPtr CopyIcon(IntPtr icon);
    [DllImport("user32.dll", SetLastError = true)] public static extern bool SetSystemCursor(IntPtr cursor, uint cursorId);
    [DllImport("user32.dll", SetLastError = true)] public static extern bool SystemParametersInfo(uint action, uint parameter, IntPtr value, uint flags);
}
"@

function Restore-SystemCursor {
    if ($script:systemCursorChanged) {
        [MSContableCursorNative]::SystemParametersInfo(0x57, 0, [IntPtr]::Zero, 0) | Out-Null
        $script:systemCursorChanged = $false
    }
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$script:form = [System.Windows.Forms.Form]::new()
$script:launchProcess = $null
$script:signalPath = Join-Path $env:TEMP ("MSContable-launch-{0}.signal" -f [guid]::NewGuid().ToString("N"))
$script:readySignalPath = Join-Path $env:TEMP ("MSContable-ready-{0}.signal" -f [guid]::NewGuid().ToString("N"))
$script:launchScript = Join-Path $PSScriptRoot "launch.ps1"
$script:powerShell = Join-Path $PSHOME "powershell.exe"
$busyCursor = [System.Windows.Forms.Cursors]::AppStarting

$script:form.Text = "MS Contable"
$script:form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::None
$script:form.StartPosition = [System.Windows.Forms.FormStartPosition]::Manual
$script:form.ShowInTaskbar = $false
$script:form.TopMost = $false
$script:form.ClientSize = [System.Drawing.Size]::new(340, 108)
$script:form.BackColor = [System.Drawing.Color]::FromArgb(38, 75, 93)
$script:form.Cursor = $busyCursor
$script:form.Font = [System.Drawing.SystemFonts]::MessageBoxFont

$content = [System.Windows.Forms.Panel]::new()
$content.Location = [System.Drawing.Point]::new(1, 1)
$content.Size = [System.Drawing.Size]::new(338, 106)
$content.BackColor = [System.Drawing.Color]::FromArgb(18, 18, 18)
$content.Cursor = $busyCursor
$script:form.Controls.Add($content)

$header = [System.Windows.Forms.Panel]::new()
$header.Location = [System.Drawing.Point]::new(0, 0)
$header.Size = [System.Drawing.Size]::new(338, 40)
$header.BackColor = [System.Drawing.Color]::FromArgb(38, 75, 93)
$header.Cursor = $busyCursor
$content.Controls.Add($header)

$brand = [System.Windows.Forms.Label]::new()
$brand.AutoSize = $true
$brand.Location = [System.Drawing.Point]::new(16, 9)
$brand.Text = "MS Contable"
$brand.Font = [System.Drawing.SystemFonts]::MessageBoxFont
$brand.ForeColor = [System.Drawing.Color]::FromArgb(255, 255, 204)
$brand.Cursor = $busyCursor
$header.Controls.Add($brand)

$status = [System.Windows.Forms.Label]::new()
$status.AutoSize = $true
$status.Location = [System.Drawing.Point]::new(17, 48)
$status.Text = "Abriendo MS Contable…"
$status.Font = [System.Drawing.Font]::new("Segoe UI", 10)
$status.ForeColor = [System.Drawing.Color]::FromArgb(238, 238, 238)
$status.Cursor = $busyCursor
$content.Controls.Add($status)

$track = [System.Windows.Forms.Panel]::new()
$track.Location = [System.Drawing.Point]::new(17, 78)
$track.Size = [System.Drawing.Size]::new(304, 4)
$track.BackColor = [System.Drawing.Color]::FromArgb(53, 53, 53)
$track.Cursor = $busyCursor
$content.Controls.Add($track)

$fill = [System.Windows.Forms.Panel]::new()
$fill.Location = [System.Drawing.Point]::new(0, 0)
$fill.Size = [System.Drawing.Size]::new(88, 4)
$fill.BackColor = [System.Drawing.Color]::FromArgb(129, 212, 250)
$fill.Cursor = $busyCursor
$track.Controls.Add($fill)

try {
    $iconPath = Join-Path $PSScriptRoot "mscontable.ico"
    if (Test-Path $iconPath -PathType Leaf) {
        $script:form.Icon = [System.Drawing.Icon]::new($iconPath)
    }
}
catch {
}

$cursorPosition = [System.Windows.Forms.Cursor]::Position
$screen = [System.Windows.Forms.Screen]::FromPoint($cursorPosition)
$workingArea = $screen.WorkingArea
$left = $workingArea.Left + [int](($workingArea.Width - $script:form.Width) / 2)
$top = $workingArea.Top + [int](($workingArea.Height - $script:form.Height) / 2)
$script:form.Location = [System.Drawing.Point]::new($left, $top)

$appStartingCursor = [MSContableCursorNative]::LoadCursor([IntPtr]::Zero, [IntPtr]32650)
if ($appStartingCursor -ne [IntPtr]::Zero) {
    $cursorCopy = [MSContableCursorNative]::CopyIcon($appStartingCursor)
    if ($cursorCopy -ne [IntPtr]::Zero) {
        $script:systemCursorChanged = [MSContableCursorNative]::SetSystemCursor($cursorCopy, 32512)
    }
}

$animationTimer = [System.Windows.Forms.Timer]::new()
$animationTimer.Interval = 24
$animationOffset = 0
$animationTimer.Add_Tick({
    $script:fill.Left = $script:animationOffset
    $script:animationOffset += 5
    if ($script:animationOffset -gt $script:track.Width) {
        $script:animationOffset = -$script:fill.Width
    }
})

$watchTimer = [System.Windows.Forms.Timer]::new()
$watchTimer.Interval = 200
$watchTimer.Add_Tick({
    if (Test-Path -LiteralPath $script:signalPath -PathType Leaf) {
        $script:watchTimer.Stop()
        $script:form.Close()
        return
    }
    if ($script:launchProcess -and $script:launchProcess.HasExited) {
        $script:watchTimer.Stop()
        $script:form.Close()
    }
})

$script:form.Add_Deactivate({
    $script:form.Hide()
})

$script:form.Add_Shown({
    $script:animationTimer.Start()
    try {
        if (-not (Test-Path $script:launchScript -PathType Leaf)) {
            throw "No se encontró el iniciador de MS Contable. Reinstalá la aplicación."
        }

        $arguments = "-NoProfile -STA -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script:launchScript`" -Action Start -SplashSignalPath `"$script:signalPath`" -SplashReadySignalPath `"$script:readySignalPath`""
        $script:launchProcess = Start-Process -FilePath $script:powerShell -ArgumentList $arguments -WindowStyle Hidden -PassThru
        $script:watchTimer.Start()
    }
    catch {
        [System.Windows.Forms.MessageBox]::Show(
            "No se pudo abrir MS Contable.`r`n`r`n$($_.Exception.Message)",
            "MS Contable",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error
        ) | Out-Null
        $script:form.Close()
    }
})

$script:form.Add_FormClosed({
    $script:animationTimer.Stop()
    $script:watchTimer.Stop()
    $script:animationTimer.Dispose()
    $script:watchTimer.Dispose()
    Remove-Item -LiteralPath $script:signalPath -Force -ErrorAction SilentlyContinue
})

[System.Windows.Forms.Application]::Run($script:form)

while ($script:launchProcess -and -not $script:launchProcess.HasExited -and -not (Test-Path -LiteralPath $script:readySignalPath -PathType Leaf)) {
    Start-Sleep -Milliseconds 200
}
Restore-SystemCursor
Remove-Item -LiteralPath $script:readySignalPath -Force -ErrorAction SilentlyContinue
$script:entryMutex.ReleaseMutex()
$script:entryMutex.Dispose()
