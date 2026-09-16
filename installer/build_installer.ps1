param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root

try {
    & $Python -m pip install --upgrade pyinstaller
    & $Python -m PyInstaller main.py --name FaceBeautyAnalysisSystem --noconfirm --clean --windowed

    $isccCandidates = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
        "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
    )
    $iscc = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $iscc) {
        throw "未找到 Inno Setup 6，请先安装后重新运行。"
    }
    & $iscc "installer\FaceBeautyAnalysisSystem.iss"

    Write-Host "安装包输出目录：$root\installer\output"
}
finally {
    Pop-Location
}
