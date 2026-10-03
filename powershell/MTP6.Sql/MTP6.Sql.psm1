Set-StrictMode -Version Latest

function Get-MTP6SqlAdapterMetadata {
    [CmdletBinding()]
    param()

    [pscustomobject]@{
        Module = 'MTP6.Sql'
        Phase = 'M0'
        DestructiveOperationsEnabled = $false
    }
}

Export-ModuleMember -Function Get-MTP6SqlAdapterMetadata
