Set-StrictMode -Version Latest

function Get-MTP6ServicesAdapterMetadata {
    [CmdletBinding()]
    param()

    [pscustomobject]@{
        Module = 'MTP6.Services'
        Phase = 'M0'
        DestructiveOperationsEnabled = $false
    }
}

Export-ModuleMember -Function Get-MTP6ServicesAdapterMetadata
