Set-StrictMode -Version Latest

function Get-MTP6NetworkAdapterMetadata {
    [CmdletBinding()]
    param()

    [pscustomobject]@{
        Module = 'MTP6.Network'
        Phase = 'M0'
        DestructiveOperationsEnabled = $false
    }
}

Export-ModuleMember -Function Get-MTP6NetworkAdapterMetadata
