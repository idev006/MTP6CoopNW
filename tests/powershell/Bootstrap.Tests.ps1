BeforeAll {
    $RepoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')
}

Describe 'MTP6 PowerShell adapter bootstrap' {
    $modules = @(
        @{ Path = 'powershell/MTP6.Network/MTP6.Network.psm1'; Function = 'Get-MTP6NetworkAdapterMetadata' },
        @{ Path = 'powershell/MTP6.Firewall/MTP6.Firewall.psm1'; Function = 'Get-MTP6FirewallAdapterMetadata' },
        @{ Path = 'powershell/MTP6.Services/MTP6.Services.psm1'; Function = 'Get-MTP6ServicesAdapterMetadata' },
        @{ Path = 'powershell/MTP6.Sql/MTP6.Sql.psm1'; Function = 'Get-MTP6SqlAdapterMetadata' }
    )

    It 'imports <Path> and reports destructive operations disabled' -ForEach $modules {
        $fullPath = Join-Path $RepoRoot $Path
        Import-Module $fullPath -Force

        $metadata = & $Function
        $metadata.Phase | Should -Be 'M0'
        $metadata.DestructiveOperationsEnabled | Should -BeFalse
    }
}
