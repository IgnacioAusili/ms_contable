$script:MSContableDataAclVersion = "3"

function Test-MSContableDataDirectoryProtection {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path
    )

    $expectedPath = [System.IO.Path]::GetFullPath(
        (Join-Path $env:LOCALAPPDATA "MSContable")
    ).TrimEnd([char]'\')
    $targetPath = [System.IO.Path]::GetFullPath($Path).TrimEnd([char]'\')
    if (-not [string]::Equals($targetPath, $expectedPath, [StringComparison]::OrdinalIgnoreCase)) {
        throw "La comprobación de permisos solo puede aplicarse a la carpeta de datos de MS Contable."
    }

    $marker = Join-Path $targetPath "data-acl-version.txt"
    if (-not (Test-Path $targetPath -PathType Container) -or -not (Test-Path $marker -PathType Leaf)) {
        return $false
    }
    $markerVersion = (Get-Content -LiteralPath $marker -Raw -ErrorAction SilentlyContinue)
    if (-not $markerVersion -or $markerVersion.Trim() -ne $script:MSContableDataAclVersion) {
        return $false
    }

    try {
        $acl = Get-Acl -LiteralPath $targetPath -ErrorAction Stop
        if (-not $acl.AreAccessRulesProtected) {
            return $false
        }

        $expectedSids = @(
            [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value,
            "S-1-5-18",
            "S-1-5-32-544"
        )
        $fullControl = [System.Security.AccessControl.FileSystemRights]::FullControl
        $containerInherit = [System.Security.AccessControl.InheritanceFlags]::ContainerInherit
        $objectInherit = [System.Security.AccessControl.InheritanceFlags]::ObjectInherit

        foreach ($rule in $acl.Access) {
            try {
                $ruleSid = $rule.IdentityReference.Translate(
                    [System.Security.Principal.SecurityIdentifier]
                ).Value
            }
            catch {
                return $false
            }

            if ($expectedSids -notcontains $ruleSid -or
                $rule.IsInherited -or
                $rule.AccessControlType -ne [System.Security.AccessControl.AccessControlType]::Allow -or
                ($rule.FileSystemRights -band $fullControl) -ne $fullControl -or
                ($rule.InheritanceFlags -band $containerInherit) -ne $containerInherit -or
                ($rule.InheritanceFlags -band $objectInherit) -ne $objectInherit) {
                return $false
            }
        }

        foreach ($sid in $expectedSids) {
            $hasPermission = $false
            foreach ($rule in $acl.Access) {
                try {
                    $ruleSid = $rule.IdentityReference.Translate(
                        [System.Security.Principal.SecurityIdentifier]
                    ).Value
                }
                catch {
                    continue
                }

                if ($ruleSid -eq $sid -and
                    $rule.AccessControlType -eq [System.Security.AccessControl.AccessControlType]::Allow -and
                    ($rule.FileSystemRights -band $fullControl) -eq $fullControl -and
                    ($rule.InheritanceFlags -band $containerInherit) -eq $containerInherit -and
                    ($rule.InheritanceFlags -band $objectInherit) -eq $objectInherit) {
                    $hasPermission = $true
                    break
                }
            }

            if (-not $hasPermission) {
                return $false
            }
        }

        return $true
    }
    catch {
        return $false
    }
}

function Protect-MSContableDataDirectory {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path,
        [switch] $Force
    )

    $expectedPath = [System.IO.Path]::GetFullPath(
        (Join-Path $env:LOCALAPPDATA "MSContable")
    ).TrimEnd([char]'\')
    $targetPath = [System.IO.Path]::GetFullPath($Path).TrimEnd([char]'\')
    if (-not [string]::Equals($targetPath, $expectedPath, [StringComparison]::OrdinalIgnoreCase)) {
        throw "La protección de permisos solo puede aplicarse a la carpeta de datos de MS Contable."
    }

    New-Item -ItemType Directory -Force -Path $targetPath | Out-Null
    if (-not $Force -and (Test-MSContableDataDirectoryProtection -Path $targetPath)) {
        return $false
    }

    $icacls = Join-Path $env:SystemRoot "System32\icacls.exe"
    if (-not (Test-Path $icacls -PathType Leaf)) {
        throw "No se encontró icacls.exe para proteger los datos de MS Contable."
    }

    $userSid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $permissions = @(
        ("*{0}:(OI)(CI)F" -f $userSid),
        "*S-1-5-18:(OI)(CI)F",
        "*S-1-5-32-544:(OI)(CI)F"
    )

    & $icacls $targetPath "/reset" "/T" "/C" "/Q" *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudieron normalizar los permisos de la carpeta de datos de MS Contable."
    }

    & $icacls $targetPath "/inheritance:r" *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo proteger la carpeta de datos de MS Contable."
    }

    $grantArguments = @($targetPath, "/grant:r") + $permissions + @("/C", "/Q")
    & $icacls @grantArguments *> $null
    if ($LASTEXITCODE -ne 0) {
        throw "No se pudo conceder acceso a la cuenta actual, SYSTEM y administradores en los datos de MS Contable."
    }

    Set-Content -LiteralPath (Join-Path $targetPath "data-acl-version.txt") `
        -Value $script:MSContableDataAclVersion `
        -Encoding ASCII
    if (-not (Test-MSContableDataDirectoryProtection -Path $targetPath)) {
        throw "Windows no confirmó los permisos esperados en los datos de MS Contable."
    }
    return $true
}
