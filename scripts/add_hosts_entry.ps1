# Add hosts entry for etusl_resultapp -> 127.0.0.1
# Run this script as Administrator. It will re-run itself with elevation if needed.

param(
    [string]$HostName = 'etu-result-app',
    [string]$Ip = '127.0.0.1'
)

function Ensure-RunAsAdmin {
    $current = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($current)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Host "Not running as Administrator. Relaunching with elevation..."
        # Use Windows PowerShell executable for elevation (works on systems without PowerShell Core)
        $psExe = (Get-Command powershell.exe -ErrorAction SilentlyContinue).Source
        if (-not $psExe) {
            Write-Error "Could not find powershell.exe to elevate. Please run this script as Administrator.";
            Exit 1
        }
        Start-Process -FilePath $psExe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
        Exit
    }
}

Ensure-RunAsAdmin

$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
$backupPath = "$hostsPath.bak.$((Get-Date).ToString('yyyyMMddHHmmss'))"

try {
    Write-Host "Backing up hosts file to: $backupPath"
    Copy-Item -Path $hostsPath -Destination $backupPath -Force
} catch {
    Write-Error "Failed to backup hosts file: $_"
    Exit 1
}

$entry = "$Ip`t$HostName"
$contents = Get-Content -Path $hostsPath -ErrorAction Stop

if ($contents -match "\b$HostName\b") {
    Write-Host "Hosts file already contains an entry for '$HostName'. Review '$hostsPath' to confirm."
    Exit 0
}

try {
    Add-Content -Path $hostsPath -Value "`n# Added by ETU_Ruslts helper script on $((Get-Date).ToString())`n$entry"
    Write-Host "Added hosts entry: $entry"
    Write-Host "Flushing DNS cache..."
    ipconfig /flushdns | Out-Null
    Write-Host "Done. You can now open http://$HostName:8000 in your browser."
} catch {
    Write-Error "Failed to update hosts file: $_"
    Exit 1
}