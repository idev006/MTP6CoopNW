BeforeAll {
    $RepoRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')
}

Describe 'MTP6.Network read-only adapter' {
    BeforeAll {
        Import-Module (Join-Path $RepoRoot 'powershell/MTP6.Network/MTP6.Network.psm1') -Force
    }

    It 'returns structured network state' {
        Mock Get-NetIPConfiguration -ModuleName MTP6.Network {
            [pscustomobject]@{
                InterfaceAlias = 'Ethernet'
                InterfaceIndex = 4
                IPv4Address = @([pscustomobject]@{ IPAddress = '192.168.1.101' })
                IPv4DefaultGateway = @([pscustomobject]@{ NextHop = '192.168.1.1' })
                DNSServer = [pscustomobject]@{ ServerAddresses = @('192.168.1.1') }
            }
        }

        $result = Get-MTP6NetworkState -InterfaceAlias 'Ethernet'

        $result.InterfaceAlias | Should -Be 'Ethernet'
        $result.InterfaceIndex | Should -Be 4
        $result.IPv4Address | Should -Contain '192.168.1.101'
        $result.IPv4DefaultGateway | Should -Contain '192.168.1.1'
        Should -Invoke Get-NetIPConfiguration -ModuleName MTP6.Network -Times 1
    }

    It 'returns structured route state' {
        Mock Get-NetRoute -ModuleName MTP6.Network {
            [pscustomobject]@{
                InterfaceIndex = 4
                DestinationPrefix = '0.0.0.0/0'
                NextHop = '192.168.1.1'
                RouteMetric = 25
                State = 'Alive'
            }
        }

        $result = Get-MTP6RouteState -InterfaceIndex 4

        $result.DestinationPrefix | Should -Be '0.0.0.0/0'
        $result.NextHop | Should -Be '192.168.1.1'
    }

    It 'reports LAN reachability without mutation' {
        Mock Test-NetConnection -ModuleName MTP6.Network { $true }

        $result = Test-MTP6LanReachability -Target '192.168.1.10'

        $result.Reachable | Should -BeTrue
        $result.Scope | Should -Be 'LAN'
    }
}

Describe 'MTP6.Firewall read-only adapter' {
    BeforeAll {
        Import-Module (Join-Path $RepoRoot 'powershell/MTP6.Firewall/MTP6.Firewall.psm1') -Force
    }

    It 'returns only project-owned firewall rules' {
        Mock Get-NetFirewallRule -ModuleName MTP6.Firewall {
            @(
                [pscustomobject]@{
                    Name = 'MTP6CoopNW-SQL'
                    DisplayName = 'MTP6CoopNW-SQL'
                    Enabled = 'True'
                    Direction = 'Inbound'
                    Action = 'Allow'
                    Profile = 'Private'
                },
                [pscustomobject]@{
                    Name = 'OtherRule'
                    DisplayName = 'OtherRule'
                    Enabled = 'True'
                    Direction = 'Inbound'
                    Action = 'Allow'
                    Profile = 'Private'
                }
            )
        }

        $result = @(Get-MTP6ManagedFirewallState)

        $result.Count | Should -Be 1
        $result[0].Name | Should -Be 'MTP6CoopNW-SQL'
    }

    It 'detects missing project-owned rules' {
        Mock Get-MTP6ManagedFirewallState -ModuleName MTP6.Firewall {
            [pscustomobject]@{ Name = 'MTP6CoopNW-SQL' }
        }

        $result = Test-MTP6FirewallDrift -ExpectedRuleName @(
            'MTP6CoopNW-SQL',
            'MTP6CoopNW-Control'
        )

        $result.DriftDetected | Should -BeTrue
        $result.MissingRule | Should -Contain 'MTP6CoopNW-Control'
    }
}

Describe 'MTP6.Services read-only adapter' {
    BeforeAll {
        Import-Module (Join-Path $RepoRoot 'powershell/MTP6.Services/MTP6.Services.psm1') -Force
    }

    It 'reports missing service without changing service state' {
        Mock Get-Service -ModuleName MTP6.Services { $null }

        $result = Get-MTP6ServiceState -Name 'MissingService'

        $result.Exists | Should -BeFalse
        $result.Status | Should -Be 'NotFound'
    }
}

Describe 'MTP6.Sql read-only adapter' {
    BeforeAll {
        Import-Module (Join-Path $RepoRoot 'powershell/MTP6.Sql/MTP6.Sql.psm1') -Force
    }

    It 'reports SQL service state' {
        Mock Get-Service -ModuleName MTP6.Sql {
            [pscustomobject]@{
                Name = 'MSSQLSERVER'
                DisplayName = 'SQL Server'
                Status = 'Running'
            }
        }

        $result = Get-MTP6SqlServiceState

        $result.Exists | Should -BeTrue
        $result.Status | Should -Be 'Running'
    }

    It 'reports SQL TCP probe' {
        Mock Test-NetConnection -ModuleName MTP6.Sql {
            [pscustomobject]@{
                TcpTestSucceeded = $true
                RemoteAddress = '192.168.1.10'
            }
        }

        $result = Test-MTP6SqlTcp -ComputerName '192.168.1.10' -Port 1433

        $result.TcpTestSucceeded | Should -BeTrue
        $result.Port | Should -Be 1433
    }
}
