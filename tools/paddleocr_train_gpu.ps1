param(
    [string]$ConfigPath = "archive\prepared\finrecon_receipt_4field_clean\paddleocr_ser\ser_vi_layoutxlm_finrecon_4field.yml"
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "paddleocr_env.ps1")

$RepoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$Python = Join-Path $RepoRoot ".venvs\paddleocr-gpu\Scripts\python.exe"
$TrainScript = Join-Path $RepoRoot "external\PaddleOCR\tools\train.py"
$Config = Join-Path $RepoRoot $ConfigPath
$DatasetDir = Split-Path -Parent $Config
$Validator = Join-Path $RepoRoot "tools\validate_paddleocr_ser_dataset.py"
$ValidationReport = Join-Path $DatasetDir "reports\paddleocr_ser_validation.json"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Missing PaddleOCR GPU Python env: $Python"
}
if (-not (Test-Path -LiteralPath $TrainScript)) {
    throw "Missing PaddleOCR train script: $TrainScript"
}
if (-not (Test-Path -LiteralPath $Config)) {
    throw "Missing PaddleOCR config: $Config"
}
if (-not (Test-Path -LiteralPath $Validator)) {
    throw "Missing PaddleOCR SER validator: $Validator"
}

& $Python $Validator --dataset-dir $DatasetDir --report $ValidationReport
if ($LASTEXITCODE -ne 0) {
    throw "PaddleOCR SER dataset validation failed. See: $ValidationReport"
}
& $Python $TrainScript -c $Config -o Global.use_gpu=True
exit $LASTEXITCODE
