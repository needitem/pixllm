param(
    [string]$ServerHost = "192.168.2.238",
    [string]$ServerUser = "root",
    [string]$ServerPassword = "",
    [string]$RemoteProjectRoot = "/root/PIX_RAG_Source",
    [ValidateSet("auto", "svn", "git", "none")]
    [string]$UpdateMode = "auto",
    [switch]$SkipUpdate,
    [switch]$SkipHealth,
    [switch]$NoBuild,
    [switch]$AppOnly,
    [switch]$SkipScriptUpload,
    [switch]$BatchMode,
    [switch]$DryRun,
    [string]$HostKeyFingerprint = "",
    [string]$PlinkPath = "",
    [string]$PscpPath = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-DeployLog {
    param([string]$Message)
    Write-Host "[deploy-win] $Message"
}

function Resolve-ToolPath {
    param(
        [string]$Preferred,
        [string]$CommandName
    )

    if ($Preferred) {
        if (-not (Test-Path $Preferred)) {
            throw "Specified path for $CommandName not found: $Preferred"
        }
        return (Resolve-Path $Preferred).Path
    }

    $cmd = Get-Command $CommandName -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "$CommandName is not available. Install PuTTY and ensure $CommandName.exe is on PATH."
    }
    return $cmd.Source
}

function New-PuTTYArgs {
    param([string]$Target)

    $args = @()
    if ($BatchMode) {
        $args += "-batch"
    }
    if ($ServerPassword) {
        $args += @("-pw", $ServerPassword)
    }
    if ($HostKeyFingerprint) {
        $args += @("-hostkey", $HostKeyFingerprint)
    }
    $args += $Target
    return $args
}

function Invoke-RemoteCommand {
    param([string]$Command)

    $target = "$ServerUser@$ServerHost"
    $args = @()
    $args += New-PuTTYArgs -Target $target
    $args += $Command

    Write-DeployLog "Remote command: $Command"
    if ($DryRun) {
        return
    }

    & $script:ResolvedPlink @args
    if ($LASTEXITCODE -ne 0) {
        throw "Remote command failed with exit code $LASTEXITCODE"
    }
}

function Copy-RemoteFile {
    param(
        [string]$LocalPath,
        [string]$RemotePath
    )

    $target = "$ServerUser@$ServerHost`:$RemotePath"
    $args = @()
    if ($BatchMode) {
        $args += "-batch"
    }
    if ($ServerPassword) {
        $args += @("-pw", $ServerPassword)
    }
    if ($HostKeyFingerprint) {
        $args += @("-hostkey", $HostKeyFingerprint)
    }
    $args += @($LocalPath, $target)

    Write-DeployLog "Upload: $LocalPath -> $target"
    if ($DryRun) {
        return
    }

    & $script:ResolvedPscp @args
    if ($LASTEXITCODE -ne 0) {
        throw "File upload failed with exit code $LASTEXITCODE"
    }
}

$script:ResolvedPlink = Resolve-ToolPath -Preferred $PlinkPath -CommandName "plink.exe"
$script:ResolvedPscp = Resolve-ToolPath -Preferred $PscpPath -CommandName "pscp.exe"

$localShellScript = Join-Path $PSScriptRoot "deploy_stack.sh"
if (-not (Test-Path $localShellScript)) {
    throw "Remote shell deploy script not found: $localShellScript"
}

$remoteShellScript = "$RemoteProjectRoot/backend/scripts/deploy_stack.sh"

$remoteArgs = @()
$remoteArgs += "--update-mode $UpdateMode"
if ($SkipUpdate) { $remoteArgs += "--skip-update" }
if ($SkipHealth) { $remoteArgs += "--skip-health" }
if ($NoBuild) { $remoteArgs += "--no-build" }
if ($AppOnly) { $remoteArgs += "--app-only" }
$remoteArgString = ($remoteArgs -join " ")

Write-DeployLog "Server: $ServerUser@$ServerHost"
Write-DeployLog "Remote project root: $RemoteProjectRoot"

if (-not $SkipScriptUpload) {
    Copy-RemoteFile -LocalPath $localShellScript -RemotePath $remoteShellScript
}

$remoteCommand = @(
    "bash -lc",
    "'cd ""$RemoteProjectRoot""",
    "&& chmod +x ""$remoteShellScript""",
    "&& ""$remoteShellScript"" $remoteArgString'"
) -join " "

Invoke-RemoteCommand -Command $remoteCommand

Write-DeployLog "Done"
