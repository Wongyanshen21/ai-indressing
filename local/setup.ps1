# AI Indressing — Local ComfyUI Setup (AMD DirectML)
# Run this in PowerShell to download and set up ComfyUI

Write-Host "=== AI Indressing Local Setup ===" -ForegroundColor Cyan
Write-Host ""

$comfyDir = Join-Path $PSScriptRoot "ComfyUI"

if (Test-Path $comfyDir) {
    Write-Host "ComfyUI already installed at $comfyDir" -ForegroundColor Green
} else {
    Write-Host "Downloading ComfyUI (DirectML version for AMD)..." -ForegroundColor Yellow

    $downloadUrl = "https://github.com/Acly/ComfyUI-directml/releases/latest/download/ComfyUI-directml-portable.zip"
    $zipPath = Join-Path $env:TEMP "ComfyUI-directml-portable.zip"

    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipPath -UseBasicParsing
        Write-Host "Extracting..." -ForegroundColor Yellow
        Expand-Archive -Path $zipPath -DestinationPath $PSScriptRoot -Force
        Remove-Item $zipPath -Force
        Write-Host "Done! ComfyUI extracted to $comfyDir" -ForegroundColor Green
    } catch {
        Write-Host "Download failed. Please install manually:" -ForegroundColor Red
        Write-Host "1. Go to: https://github.com/Acly/ComfyUI-directml/releases" -ForegroundColor White
        Write-Host "2. Download ComfyUI-directml-portable.zip" -ForegroundColor White
        Write-Host "3. Extract to: $comfyDir" -ForegroundColor White
        exit 1
    }
}

Write-Host ""
Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Run ComfyUI:" -ForegroundColor White
Write-Host "   .\local\ComfyUI\run_nvidia_gpu.bat" -ForegroundColor Green
Write-Host ""
Write-Host "2. Open in browser: http://127.0.0.1:8188" -ForegroundColor White
Write-Host ""
Write-Host "3. Install FLUX.1 Fill model:" -ForegroundColor White
Write-Host "   - In ComfyUI Manager -> Install Custom Nodes -> search 'FLUX.1 Fill'" -ForegroundColor White
Write-Host "   - Or manually download to ComfyUI/models/checkpoints/" -ForegroundColor White
Write-Host ""
Write-Host "4. Load the workflow file: local/comfyui_workflow.json" -ForegroundColor White
Write-Host ""
Write-Host "5. Upload your photo, mask, and run!" -ForegroundColor White
