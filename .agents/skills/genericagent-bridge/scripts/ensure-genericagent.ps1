param(
    [string]$RepoRoot = "D:\erp",
    [switch]$ForceRefresh
)

$ErrorActionPreference = "Stop"

$externalRoot = Join-Path $RepoRoot "external"
$targetDir = Join-Path $externalRoot "GenericAgent"
$zipPath = Join-Path $env:TEMP "GenericAgent-main.zip"
$extractRoot = Join-Path $env:TEMP ("GenericAgent-extract-" + [guid]::NewGuid().ToString("N"))
$downloadUrl = "https://codeload.github.com/lsdefine/GenericAgent/zip/refs/heads/main"

New-Item -ItemType Directory -Force -Path $externalRoot | Out-Null

if ((Test-Path $targetDir) -and (-not $ForceRefresh)) {
    Write-Output "GenericAgent already exists at $targetDir"
    exit 0
}

if (Test-Path $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}
if (Test-Path $extractRoot) {
    Remove-Item -LiteralPath $extractRoot -Recurse -Force
}

Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath
Expand-Archive -LiteralPath $zipPath -DestinationPath $extractRoot -Force

$expandedDir = Join-Path $extractRoot "GenericAgent-main"
if (-not (Test-Path $expandedDir)) {
    throw "Downloaded archive does not contain GenericAgent-main"
}

if (Test-Path $targetDir) {
    Remove-Item -LiteralPath $targetDir -Recurse -Force
}

Move-Item -LiteralPath $expandedDir -Destination $targetDir

Remove-Item -LiteralPath $zipPath -Force
Remove-Item -LiteralPath $extractRoot -Recurse -Force

Write-Output "GenericAgent ready at $targetDir"
