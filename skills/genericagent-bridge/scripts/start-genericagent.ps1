param(
    [ValidateSet("cli", "ui")]
    [string]$Mode = "cli",
    [string]$RepoRoot = "D:\erp"
)

$ErrorActionPreference = "Stop"

$targetDir = Join-Path (Join-Path $RepoRoot "external") "GenericAgent"
$mykeyPath = Join-Path $targetDir "mykey.py"
$agentMain = Join-Path $targetDir "agentmain.py"
$launchUi = Join-Path $targetDir "launch.pyw"

if (-not (Test-Path $targetDir)) {
    throw "GenericAgent checkout not found at $targetDir"
}

if (-not (Test-Path $mykeyPath)) {
    throw "GenericAgent is not configured yet. Create mykey.py from mykey_template.py first."
}

if ($Mode -eq "cli") {
    if (-not (Test-Path $agentMain)) {
        throw "agentmain.py not found"
    }
    Set-Location $targetDir
    python .\agentmain.py
    exit $LASTEXITCODE
}

if (-not (Test-Path $launchUi)) {
    throw "launch.pyw not found"
}

Start-Process -FilePath "python" -ArgumentList ".\launch.pyw" -WorkingDirectory $targetDir
Write-Output "GenericAgent UI launch requested from $targetDir"
