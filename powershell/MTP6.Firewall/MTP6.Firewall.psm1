Set-StrictMode -Version Latest

function Get-MTP6FirewallAdapterInfo {
    [CmdletBinding()]
    param()

    [pscustomobject]@{
        Module = 'MTP6.Firewall'
        Phase = 'M4'
        DestructiveOperationsEnabled = $false
    }
}

function Get-MTP6ManagedFirewallState {
    [CmdletBinding()]
    param(
        [string]$Prefix = 'MTP6CoopNW-'
    )

    $rules = @(
        Get-NetFirewallRule -ErrorAction Stop |
            Where-Object { $_.DisplayName -like "$Prefix*" }
    )

    foreach ($rule in $rules) {
        [pscustomobject]@{
            Name = $rule.Name
            DisplayName = $rule.DisplayName
            Enabled = [string]$rule.Enabled
            Direction = [string]$rule.Direction
            Action = [string]$rule.Action
            Profile = [string]$rule.Profile
        }
    }
}

function Test-MTP6FirewallDrift {
    [CmdletBinding()]
    param(
        [string[]]$ExpectedRuleName = @(),
        [string]$Prefix = 'MTP6CoopNW-'
    )

    $actual = @(Get-MTP6ManagedFirewallState -Prefix $Prefix)
    $actualNames = @($actual | ForEach-Object { $_.Name })

    $missing = @($ExpectedRuleName | Where-Object { $_ -notin $actualNames })
    $unexpected = @($actualNames | Where-Object { $_ -notin $ExpectedRuleName })

    [pscustomobject]@{
        DriftDetected = ($missing.Count -gt 0 -or $unexpected.Count -gt 0)
        MissingRule = $missing
        UnexpectedRule = $unexpected
        ActualRuleCount = $actualNames.Count
    }
}

Export-ModuleMember -Function @(
    'Get-MTP6FirewallAdapterInfo',
    'Get-MTP6ManagedFirewallState',
    'Test-MTP6FirewallDrift'
)
