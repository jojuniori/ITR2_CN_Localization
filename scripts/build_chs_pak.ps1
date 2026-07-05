param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$Version,
    [string]$VersionFile
)

$ErrorActionPreference = "Stop"

function Normalize-Version {
    param([string]$Value)

    if ($Value -notmatch '^v?(\d+)\.(\d+)\.(\d+)$') {
        throw "Invalid version '$Value'. Expected format like v0.3.1 or 0.3.1."
    }

    return "v$($Matches[1]).$($Matches[2]).$($Matches[3])"
}

function Get-NextPatchVersion {
    param([string]$Value)

    $normalized = Normalize-Version $Value
    if ($normalized -notmatch '^v(\d+)\.(\d+)\.(\d+)$') {
        throw "Invalid version '$Value'."
    }

    $major = [int]$Matches[1]
    $minor = [int]$Matches[2]
    $patch = [int]$Matches[3]

    $patch += 1
    if ($patch -gt 9) {
        $patch = 0
        $minor += 1
    }
    if ($minor -gt 9) {
        $minor = 0
        $major += 1
    }

    return "v$major.$minor.$patch"
}

$autoVersion = -not $PSBoundParameters.ContainsKey("Version")
if ([string]::IsNullOrWhiteSpace($VersionFile)) {
    $VersionFile = Join-Path $Root "VERSION"
}

if ($autoVersion) {
    if (-not (Test-Path $VersionFile)) {
        throw "Missing version file: $VersionFile"
    }
    $Version = (Get-Content -LiteralPath $VersionFile -Raw).Trim()
}

$Version = Normalize-Version $Version
$nextVersion = Get-NextPatchVersion $Version

$stage = Join-Path $Root "build\stage"
$pakName = "z_IntoTheRadius2_SimplifiedChinese_Localization_P.pak"
$pakOut = Join-Path $Root "build\$pakName"
$dist = Join-Path $Root "dist"
$reports = Join-Path $Root "build\reports"
$zipStage = Join-Path $Root "build\vortex_zip_stage"
$distZip = Join-Path $dist "IntoTheRadius2_SimplifiedChinese_Localization_$Version.zip"
$master = Join-Path $Root "translation\ITR2_CN_master.csv"
$builtLocresCsv = Join-Path $reports "ITR2_CN_built_locres_audit.csv"
$legacyBuiltLocresCsv = Join-Path $Root "translation\ITR2_CN_built_locres.csv"
$mapleLicense = Join-Path $Root "licenses\MapleMono-OFL.txt"

if (Test-Path $stage) {
    Remove-Item -LiteralPath $stage -Recurse -Force
}
if (Test-Path $pakOut) {
    Remove-Item -LiteralPath $pakOut -Force
}
if (Test-Path $zipStage) {
    Remove-Item -LiteralPath $zipStage -Recurse -Force
}
if (Test-Path $distZip) {
    Remove-Item -LiteralPath $distZip -Force
}
if (Test-Path $legacyBuiltLocresCsv) {
    Remove-Item -LiteralPath $legacyBuiltLocresCsv -Force
}

New-Item -ItemType Directory -Force -Path (Join-Path $stage "Localization\Game\en") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $stage "ITR2\Fonts") | Out-Null
New-Item -ItemType Directory -Force -Path $dist | Out-Null
New-Item -ItemType Directory -Force -Path $reports | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $zipStage "LICENSES") | Out-Null

if (-not (Test-Path $mapleLicense)) {
    throw "Missing Maple Mono license file: $mapleLicense"
}

python (Join-Path $Root "scripts\refresh_master_csv.py")

python (Join-Path $Root "scripts\build_locres_from_master.py") `
    --master $master `
    --output (Join-Path $stage "Localization\Game\en\Game.locres")

$userFonts = Join-Path $env:LOCALAPPDATA "Microsoft\Windows\Fonts"
$mapleSemiBold = Join-Path $userFonts "MapleMono-NF-CN-SemiBold.ttf"
$mapleBold = Join-Path $userFonts "MapleMono-NF-CN-Bold.ttf"
$mapleRegular = Join-Path $userFonts "MapleMono-NF-CN-Regular.ttf"

if ((Test-Path $mapleSemiBold) -and (Test-Path $mapleBold) -and (Test-Path $mapleRegular)) {
    Copy-Item -LiteralPath $mapleSemiBold -Destination (Join-Path $stage "ITR2\Fonts\NEXT_ART_SemiBold.ufont") -Force
    Copy-Item -LiteralPath $mapleBold -Destination (Join-Path $stage "ITR2\Fonts\PTSansNarrow-Bold.ufont") -Force
    Copy-Item -LiteralPath $mapleRegular -Destination (Join-Path $stage "ITR2\Fonts\PTSansNarrow-Regular.ufont") -Force
}
else {
    throw "Missing Maple Mono NF CN fonts in $userFonts. Install MapleMono-NF-CN-Regular.ttf, MapleMono-NF-CN-Bold.ttf, and MapleMono-NF-CN-SemiBold.ttf before building."
}

& (Join-Path $Root "tools\repak\repak.exe") pack --version V7 --compression Zlib --mount-point "../../../IntoTheRadius2/Content/" $stage $pakOut

python (Join-Path $Root "scripts\locres_tool.py") export-csv (Join-Path $stage "Localization\Game\en\Game.locres") $builtLocresCsv

Copy-Item -LiteralPath $pakOut -Destination (Join-Path $zipStage $pakName) -Force
Copy-Item -LiteralPath $mapleLicense -Destination (Join-Path $zipStage "LICENSES\MapleMono-OFL.txt") -Force
Compress-Archive -LiteralPath (Join-Path $zipStage $pakName), (Join-Path $zipStage "LICENSES") -DestinationPath $distZip -Force

if ($autoVersion) {
    Set-Content -LiteralPath $VersionFile -Value $nextVersion -NoNewline -Encoding utf8NoBOM
}

Write-Host "Built: $pakOut"
Write-Host "Packaged: $distZip"
if ($autoVersion) {
    Write-Host "Version file advanced: $Version -> $nextVersion"
}
else {
    Write-Host "Version override used: $Version"
}
Write-Host "Master CSV: $master"
Write-Host "Built locres CSV: $builtLocresCsv"
