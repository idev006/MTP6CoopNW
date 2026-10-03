[CmdletBinding()]
param(
    [switch]$SkipPython,
    [switch]$SkipPowerShell
)

$ErrorActionPreference = 'Stop'
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')
Push-Location $repoRoot

try {
    if (-not $SkipPython) {
        python -m pytest -m "not destructive"
        if ($LASTEXITCODE -ne 0) { throw "Python tests failed." }
    }

    if (-not $SkipPowerShell) {
        if (-not (Get-Module -ListAvailable -Name Pester)) {
            throw "Pester is required. Install Pester 5+ before running PowerShell tests."
        }
        Invoke-Pester -Path 'tests/powershell' -CI
    }
}
finally {
    Pop-Location
}
