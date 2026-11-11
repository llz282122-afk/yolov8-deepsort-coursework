param(
    [string]$Python = "python",
    [string]$Source = "MVI_20011.mp4",
    [switch]$BaselineOnly
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "../../../..")).Path
$pythonPath = (Get-Command $Python -CommandType Application -ErrorAction Stop).Source
$previousPythonPath = $env:PYTHONPATH

function Invoke-Experiment($Model, $Confidence, $Name) {
    & $pythonPath -B predict.py "model=$Model" "source=$Source" "conf=$Confidence" "iou=0.7" "imgsz=640" "project=runs/reproduction" "name=$Name" "save=True"
    if ($LASTEXITCODE -ne 0) {
        throw "Experiment $Name failed with exit code $LASTEXITCODE."
    }
}

Push-Location -LiteralPath $PSScriptRoot
try {
    $env:PYTHONPATH = $repoRoot
    $requiredFiles = @($Source, "yolov8n.pt", "deep_sort_pytorch/deep_sort/deep/checkpoint/ckpt.t7")
    if (-not $BaselineOnly) {
        $requiredFiles += "yolov8s.pt"
    }
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            throw "Required file is missing: $file"
        }
    }
    Invoke-Experiment "yolov8n.pt" "0.5" "baseline_yolov8n_conf05"
    if (-not $BaselineOnly) {
        Invoke-Experiment "yolov8s.pt" "0.5" "model_yolov8s_conf05"
        Invoke-Experiment "yolov8n.pt" "0.3" "conf03"
        Invoke-Experiment "yolov8n.pt" "0.7" "conf07"
    }
} finally {
    $env:PYTHONPATH = $previousPythonPath
    Pop-Location
}
