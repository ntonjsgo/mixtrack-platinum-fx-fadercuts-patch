# Extracts the original 1.10 firmware (.bin) from Numark's Windows installer without installing anything.
#
# Usage: .\extract_from_windows_installer.ps1 -Installer "Install MixTrack Platinum FX Firmware Updater For Firmware 1.10.exe" -Out fw.bin
#
# The installer carries the MSI packages as PE resources; the 64-bit MSI is carved out, its Installer.cab
# stream is read through the Windows Installer API (read-only) and expanded with expand.exe.
param(
    [Parameter(Mandatory = $true)][string]$Installer,
    [Parameter(Mandatory = $true)][string]$Out
)
$ErrorActionPreference = "Stop"

$InstallerSha256 = "9521721b33771bcc52077f2c24dc593880726c5319e7a371221cf7509eebaf79"
$FirmwareSha256 = "691c612d34fd4c3e275e52fd4735276f52a64fe6d5c4809cf58bac3b747ffb26"
$MsiOffset = 17864736   # resource MSI/MSI64
$MsiLength = 2453504

if ((Get-FileHash -Algorithm SHA256 $Installer).Hash.ToLower() -ne $InstallerSha256) {
    throw "This is not the official 1.10 Windows installer."
}

$work = Join-Path ([IO.Path]::GetTempPath()) ("mpfx-" + [Guid]::NewGuid())
New-Item -ItemType Directory $work | Out-Null
try {
    $bytes = [IO.File]::ReadAllBytes((Resolve-Path $Installer))
    $msi = Join-Path $work "updater64.msi"
    [IO.File]::WriteAllBytes($msi, $bytes[$MsiOffset..($MsiOffset + $MsiLength - 1)])

    $wi = New-Object -ComObject WindowsInstaller.Installer
    $db = $wi.OpenDatabase($msi, 0)
    $view = $db.OpenView("SELECT Data FROM _Streams WHERE Name='Installer.cab'")
    $view.Execute()
    $rec = $view.Fetch()
    $cab = $rec.ReadStream(1, $rec.DataSize(1), 1)
    $cabPath = Join-Path $work "Installer.cab"
    [IO.File]::WriteAllBytes($cabPath, [Text.Encoding]::GetEncoding(28591).GetBytes($cab))
    $view.Close()
    foreach ($o in @($rec, $view, $db, $wi)) { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($o) }
    $rec = $view = $db = $wi = $null
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()

    expand.exe $cabPath -F:FirmwareFile $work | Out-Null
    $fw = Join-Path $work "FirmwareFile"
    if ((Get-FileHash -Algorithm SHA256 $fw).Hash.ToLower() -ne $FirmwareSha256) {
        throw "Extracted firmware does not match the official 1.10 image."
    }
    Copy-Item $fw $Out
    Write-Output "Firmware 1.10 written to $Out"
}
finally {
    Remove-Item -Recurse -Force $work
}
