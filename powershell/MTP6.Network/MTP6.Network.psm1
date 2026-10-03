Set-StrictMode -Version Latest

function Get-MTP6NetworkAdapterInfo {
    [CmdletBinding()]
    param()

    [pscustomobject]@{
        Module = 'MTP6.Network'
        Phase = 'M4'
        DestructiveOperationsEnabled = $false
    }
}

function Get-MTP6NetworkState {
    [CmdletBinding()]
    param(
        [string]$InterfaceAlias
    )

    if ($InterfaceAlias) {
        $configs = @(Get-NetIPConfiguration -InterfaceAlias $InterfaceAlias -ErrorAction Stop)
    }
    else {
        $configs = @(Get-NetIPConfiguration -ErrorAction Stop)
    }

    foreach ($config in $configs) {
        [pscustomobject]@{
            InterfaceAlias = $config.InterfaceAlias
            InterfaceIndex = $config.InterfaceIndex
            IPv4Address = @($config.IPv4Address | ForEach-Object { $_.IPAddress })
            IPv4DefaultGateway = @(
                $config.IPv4DefaultGateway | ForEach-Object { $_.NextHop }
            )
            DnsServer = @($config.DNSServer.ServerAddresses)
        }
    }
}

function Get-MTP6RouteState {
    [CmdletBinding()]
    param(
        [int]$InterfaceIndex
    )

    if ($InterfaceIndex -gt 0) {
        $routes = @(Get-NetRoute -AddressFamily IPv4 -InterfaceIndex $InterfaceIndex -ErrorAction Stop)
    }
    else {
        $routes = @(Get-NetRoute -AddressFamily IPv4 -ErrorAction Stop)
    }

    foreach ($route in $routes) {
        [pscustomobject]@{
            InterfaceIndex = $route.InterfaceIndex
            DestinationPrefix = $route.DestinationPrefix
            NextHop = $route.NextHop
            RouteMetric = $route.RouteMetric
            State = $route.State
        }
    }
}

function Test-MTP6LanReachability {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Target
    )

    $reachable = Test-NetConnection -ComputerName $Target -InformationLevel Quiet -WarningAction SilentlyContinue

    [pscustomobject]@{
        Target = $Target
        Reachable = [bool]$reachable
        Scope = 'LAN'
    }
}

function Test-MTP6InternetReachability {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$Target
    )

    $reachable = Test-NetConnection -ComputerName $Target -InformationLevel Quiet -WarningAction SilentlyContinue

    [pscustomobject]@{
        Target = $Target
        Reachable = [bool]$reachable
        Scope = 'Internet'
    }
}

Export-ModuleMember -Function @(
    'Get-MTP6NetworkAdapterInfo',
    'Get-MTP6NetworkState',
    'Get-MTP6RouteState',
    'Test-MTP6LanReachability',
    'Test-MTP6InternetReachability'
)
