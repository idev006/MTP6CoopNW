Set-StrictMode -Version Latest

function Get-MTP6ServiceAdapterInfo {
    [CmdletBinding()]
    param()

    [pscustomobject]@{
        Module = 'MTP6.Services'
        Phase = 'M0'
        DestructiveOperationsEnabled = $false
    }
}

Export-ModuleMember -Function Get-MTP6ServiceAdapterInfo
