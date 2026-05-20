param(
    [string]$RepoRoot = "D:\erp"
)

$targetDir = Join-Path (Join-Path $RepoRoot "external") "GenericAgent"
$mykeyPath = Join-Path $targetDir "mykey.py"
$templatePath = Join-Path $targetDir "mykey_template.py"
$agentMain = Join-Path $targetDir "agentmain.py"
$launchUi = Join-Path $targetDir "launch.pyw"

[pscustomobject]@{
    RepoPath = $targetDir
    RepoExists = (Test-Path $targetDir)
    AgentMainExists = (Test-Path $agentMain)
    LaunchUiExists = (Test-Path $launchUi)
    MyKeyExists = (Test-Path $mykeyPath)
    MyKeyTemplateExists = (Test-Path $templatePath)
} | Format-List
