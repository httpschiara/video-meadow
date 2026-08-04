param(
    [Parameter(Mandatory = $true)]
    [string]$AppDirectory
)

$resolvedAppDirectory = (Resolve-Path -LiteralPath $AppDirectory).Path
$launcherPath = Join-Path $resolvedAppDirectory "run_video_meadow.bat"
$iconPath = Join-Path $resolvedAppDirectory "video_meadow_pirate_icon_chunky.ico"
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Video Meadow.lnk"

if (-not (Test-Path -LiteralPath $launcherPath)) {
    throw "Launcher not found: $launcherPath"
}

if (-not (Test-Path -LiteralPath $iconPath)) {
    throw "Icon not found: $iconPath"
}

if (Test-Path -LiteralPath $shortcutPath) {
    Remove-Item -LiteralPath $shortcutPath -Force
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $env:ComSpec
$shortcut.Arguments = '/c ""' + $launcherPath + '""'
$shortcut.WorkingDirectory = $resolvedAppDirectory
$shortcut.IconLocation = "$iconPath,0"
$shortcut.Description = "Launch Video Meadow"
$shortcut.Save()

$savedShortcut = $shell.CreateShortcut($shortcutPath)
if ($savedShortcut.IconLocation -notlike "$iconPath*") {
    throw "The shortcut was created, but its icon could not be set: $($savedShortcut.IconLocation)"
}

Write-Output "Shortcut created: $shortcutPath"
