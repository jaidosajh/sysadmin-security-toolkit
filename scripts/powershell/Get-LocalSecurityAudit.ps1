#Requires -Version 5.1
<#
.SYNOPSIS
  Read-only inventory of local Windows accounts and Administrators membership.
.DESCRIPTION
  Requires Microsoft.PowerShell.LocalAccounts on Windows. Does not change settings.
.PARAMETER OutputPath
  Optional JSON report path; reports may contain sensitive administrative metadata.
#>
[CmdletBinding()]
param([string]$OutputPath)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not (Get-Command Get-LocalUser -ErrorAction SilentlyContinue)) {
    throw 'Get-LocalUser is unavailable. Use supported PowerShell on Windows.'
}
$users = @(Get-LocalUser | Select-Object Name, Enabled, LastLogon, PasswordRequired, PasswordExpires)
$group = Get-LocalGroup -SID 'S-1-5-32-544'
$admins = @(Get-LocalGroupMember -Group $group.Name | Select-Object Name, ObjectClass, PrincipalSource)
$report = [ordered]@{
    ComputerName = $env:COMPUTERNAME
    CollectedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
    LocalUsers = $users
    LocalAdministrators = $admins
    Note = 'Read-only inventory; review according to your organizational policies.'
}
$json = $report | ConvertTo-Json -Depth 5
if ($OutputPath) {
    $json | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    Write-Host "Report written to $OutputPath"
} else {
    $json
}
