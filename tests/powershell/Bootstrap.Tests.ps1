BeforeAll {
    $RepoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')
}

Describe 'MTP6 PowerShell adapter bootstrap' {
    $modules = @(
        @{ Path = 'powershell/MTP6.Network/MTP6.Network.psm1'; Function = 'Get-MTP6NetworkAdapterInfo' },
        @{ Path = 'powershell/MTP6.Firewall/MTP6.Firewall.psm1'; Function = 'Get-MTP6FirewallAdapterInfo' },
        @{ Path = 'powershell/MTP6.Services/MTP6.Services.psm1'; Function = 'Get-MTP6ServiceAdapterInfo' },
        @{ Path = 'powershell/MTP6.Sql/MTP6.Sql.psm1'; Function = 'Get-MTP6SqlAdapterInfo' }
    )

    It 'imports <Path> and reports destructive operations disabled' -ForEach $modules {
        $fullPath = Join-Path $RepoRoot $Path
        Import-Module $fullPath -Force

        $metadata = & $Function
        $metadata.Phase | Should -Be 'M4'
        $metadata.DestructiveOperationsEnabled | Should -BeFalse
    }
}
