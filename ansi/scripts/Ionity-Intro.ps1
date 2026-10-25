<#
 =============================================================================
  IONITY GLOBAL / AEDI  ::  PowerShell terminal intro
  Author: Johan Wilhelm van Antwerp | Ionity (Pty) Ltd | Policy 986 AED
  (c) 2018-2026 Antwerp Designs | Ionity (Pty) Ltd - All Rights Reserved - TM2
  usage: .\Ionity-Intro.ps1 -Cols 100
 =============================================================================
#>
param([ValidateSet(60,100,160)][int]$Cols = 100)
$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
Clear-Host
$banner = Join-Path $here '..\banners\ionity-global-banner.ans'
$art    = Join-Path $here "..\logos\ionity-global-logo-${Cols}col.ans"
foreach ($f in @($banner, $art)) {
    if (Test-Path $f) { Get-Content -Raw -Encoding UTF8 $f | Write-Host; "" | Write-Host }
}
Write-Host "  Building Tomorrow, Today.   Anything is Possible with God." -ForegroundColor Cyan
Write-Host "  www.ionity.today | Policy 986 AED | TM2"  -ForegroundColor DarkGray
