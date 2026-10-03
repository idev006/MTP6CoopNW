Set-StrictMode -Version Latest

function Get-MTP6ServiceAdapterInfo {
    [CmdletBinding()]
    param()

    [pscustomobject]@{
        Module = 'MTP6.Services'
        Phase = 'M4'
        DestructiveOperationsEnabled = $false
    }
}

function Get-MTP6ServiceState {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string[]]$Name
    )

    foreach ($serviceName in $Name) {
        $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
        if ($null -eq $service) {
            [pscustomobject]@{
                Name = $serviceName
                Exists = $false
                Status = 'NotFound'
            }
            continue
        }

        [pscustomobject]@{
            Name = $service.Name
            DisplayName = $service.DisplayName
            Exists = $true
            Status = [string]$service.Status
        }
    }
}

Export-ModuleMember -Function @(
    'Get-MTP6ServiceAdapterInfo',
    'Get-MTP6ServiceState'
)
