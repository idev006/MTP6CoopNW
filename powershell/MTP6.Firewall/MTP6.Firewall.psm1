Set-StrictMode -Version Latest

function Get-MTP6FirewallAdapterInfo {
    [CmdletBinding()]
    param()

    [pscustomobject]@{
        Module = 'MTP6.Firewall'
        Phase = 'M0'
        DestructiveOperationsEnabled = $false
    }
}

Export-ModuleMember -Function Get-MTP6FirewallAdapterInfo
