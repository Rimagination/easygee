param(
  [string]$PluginDir = (Join-Path $HOME "plugins\easygee"),
  [string]$Repo = "https://github.com/Rimagination/easygee.git",
  [string]$Branch = "main",
  [switch]$SkipPull,
  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$InstallArgs
)

# Windows convenience wrapper: clone or update EasyGEE, then run scripts/install.py
# (Python runtime + registration with every detected agent host).
$ErrorActionPreference = "Stop"

if (Test-Path (Join-Path $PluginDir ".git")) {
  if (-not $SkipPull) {
    git -C $PluginDir pull --ff-only origin $Branch
  }
} elseif (Test-Path $PluginDir) {
  throw "Target exists but is not a git checkout: $PluginDir"
} else {
  git clone --branch $Branch $Repo $PluginDir
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  throw "Python 3.9+ is required on PATH to run the installer."
}
& $python.Source (Join-Path $PluginDir "scripts\install.py") @InstallArgs
exit $LASTEXITCODE
