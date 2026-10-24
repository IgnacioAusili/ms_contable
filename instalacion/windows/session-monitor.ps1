function Signal-BrowserPageReady {
    param(
        [string] $HeartbeatDir,
        [string] $SignalPath,
        [int] $TimeoutSeconds = 25
    )

    if ([string]::IsNullOrWhiteSpace($SignalPath)) {
        return
    }

    $clock = [System.Diagnostics.Stopwatch]::StartNew()
    while ($clock.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
        $activeSession = Get-ChildItem -LiteralPath $HeartbeatDir -Filter "*.active" -File -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($activeSession) {
            Write-StartupLog -Message ("La página final notificó que está lista en {0} ms" -f $clock.ElapsedMilliseconds)
            break
        }
        Start-Sleep -Milliseconds 200
    }

    if ($clock.Elapsed.TotalSeconds -ge $TimeoutSeconds) {
        Write-StartupLog -Message "La página final no notificó su carga dentro del tiempo previsto"
    }
    [System.IO.File]::WriteAllText($SignalPath, "ready", [System.Text.UTF8Encoding]::new($false))
}

function Wait-ForBrowserSessionsToClose {
    param(
        [string] $HeartbeatDir,
        [string] $WaitressPidFile,
        [string] $CaddyPidFile,
        [string] $Python,
        [string] $Caddy,
        [string] $RuntimeCaddyfile
    )

    Write-StartupLog -Message "Se monitorea la actividad de las páginas abiertas para cerrar los servicios al salir"
    $inactiveSince = $null
    while ($true) {
        Start-Sleep -Seconds 5

        $waitressId = [int](Get-Content -LiteralPath $WaitressPidFile -Raw -ErrorAction SilentlyContinue)
        $caddyId = [int](Get-Content -LiteralPath $CaddyPidFile -Raw -ErrorAction SilentlyContinue)
        $activeWaitress = Get-ManagedProcess -ProcessId $waitressId -Executable $Python -CommandMarker "ms_contable.wsgi:application"
        $activeCaddy = Get-ManagedProcess -ProcessId $caddyId -Executable $Caddy -CommandMarker @($RuntimeCaddyfile, (Join-Path (Split-Path -Parent $Caddy) "Caddyfile"))
        if (-not $activeWaitress -or -not $activeCaddy) {
            Write-StartupLog -Message "Se detectó que uno de los servicios locales terminó; se detendrá la instancia restante"
            return
        }

        $now = [DateTime]::UtcNow
        $activeSessions = @(Get-ChildItem -LiteralPath $HeartbeatDir -Filter "*.active" -File -ErrorAction SilentlyContinue |
            Where-Object { ($now - $_.LastWriteTimeUtc).TotalSeconds -lt 120 })
        if ($activeSessions.Count -gt 0) {
            $inactiveSince = $null
            continue
        }
        if (-not $inactiveSince) {
            $inactiveSince = $now
        }
        elseif (($now - $inactiveSince).TotalSeconds -ge 30) {
            Write-StartupLog -Message "No quedan páginas activas de MS Contable; se apagarán Waitress y Caddy"
            return
        }
    }
}
