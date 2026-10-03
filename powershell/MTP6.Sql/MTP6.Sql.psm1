Set-StrictMode -Version Latest

function Get-MTP6SqlAdapterInfo {
    [CmdletBinding()]
    param()

    [pscustomobject]@{
        Module = 'MTP6.Sql'
        Phase = 'M4'
        DestructiveOperationsEnabled = $false
    }
}

function Get-MTP6SqlServiceState {
    [CmdletBinding()]
    param(
        [string]$ServiceName = 'MSSQLSERVER'
    )

    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($null -eq $service) {
        return [pscustomobject]@{
            Name = $ServiceName
            Exists = $false
            Status = 'NotFound'
        }
    }

    [pscustomobject]@{
        Name = $service.Name
        DisplayName = $service.DisplayName
        Exists = $true
        Status = [string]$service.Status
    }
}

function Test-MTP6SqlTcp {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ComputerName,

        [ValidateRange(1, 65535)]
        [int]$Port = 1433
    )

    $result = Test-NetConnection -ComputerName $ComputerName -Port $Port -WarningAction SilentlyContinue -InformationLevel Detailed

    [pscustomobject]@{
        ComputerName = $ComputerName
        Port = $Port
        TcpTestSucceeded = [bool]$result.TcpTestSucceeded
        RemoteAddress = if ($null -ne $result.RemoteAddress) {
            [string]$result.RemoteAddress
        }
        else {
            $null
        }
    }
}

Export-ModuleMember -Function @(
    'Get-MTP6SqlAdapterInfo',
    'Get-MTP6SqlServiceState',
    'Test-MTP6SqlTcp'
)
