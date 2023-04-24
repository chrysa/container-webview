param([switch]$Elevated)
function Test-Admin
{
    $currentUser = New-Object Security.Principal.WindowsPrincipal $([Security.Principal.WindowsIdentity]::GetCurrent() )
    $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

function CreateLine
{
    param (
        [String]$NDD
    )
    Write-Output "create line  '127.0.0.1       $NDD'"
    Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value "127.0.0.1       $NDD"
}

if ((Test-Admin) -eq $false)
{
    if ($elevated)
    {
        # tried to elevate, did not work, aborting
    }
    else
    {
        Start-Process powershell.exe -Verb RunAs -ArgumentList ('-noprofile -noexit -file "{0}" -elevated ' -f ($myinvocation.MyCommand.Definition))
    }
    exit
}


$ScriptPath = Split-Path  $MyInvocation.MyCommand.Path

if (-not((Get-Content "C:\Windows\System32\drivers\etc\hosts" | Select-String -Pattern "127.0.0.1       docker.internal").Matches.Success))
{
    CreateLine -NDD docker.internal
}

Add-Content -Path "C:\Windows\System32\drivers\etc\hosts" -Value "# docker overview"
Select-String -Path "$( $ScriptPath )\..\.env" -Pattern "_PREFIX_URL" | ForEach-Object {
    $NDD = $_.Line.split("=")[1]
    Get-Content "C:\Windows\System32\drivers\etc\hosts"
    Write-Output $NDD
    if (-not((Get-Content "C:\Windows\System32\drivers\etc\hosts" | Select-String -Pattern "127.0.0.1       $NDD.docker.internal").Matches.Success))
    {
        CreateLine -NDD "$NDD.docker.internal"
    }
    Get-Content "C:\Windows\System32\drivers\etc\hosts"
}

# Start-Sleep 2

# Stop-Process -Name "powershell"
