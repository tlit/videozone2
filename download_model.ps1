$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) {
    $ScriptDir = Get-Location
}

$ModelId = "SimianLuo/LCM_Dreamshaper_v7"
$BaseUrl = "https://huggingface.co/$ModelId/resolve/main"
# Fix: Join-Path in PS 5.1 doesn't support multiple args. Construct path with backslashes.
$OutputDir = Join-Path $ScriptDir "models\SimianLuo\LCM_Dreamshaper_v7"

# File list
$Files = @(
    "model_index.json",
    "scheduler/scheduler_config.json",
    "feature_extractor/preprocessor_config.json",
    "tokenizer/tokenizer_config.json",
    "tokenizer/vocab.json",
    "tokenizer/merges.txt",
    "tokenizer/special_tokens_map.json",
    "text_encoder/config.json",
    "text_encoder/model.fp16.safetensors",
    "unet/config.json",
    "unet/diffusion_pytorch_model.fp16.safetensors",
    "vae/config.json",
    "vae/diffusion_pytorch_model.fp16.safetensors"
)

Write-Host "Starting download for $ModelId..." -ForegroundColor Cyan
Write-Host "Target Directory: $OutputDir" -ForegroundColor Gray

if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
}

foreach ($File in $Files) {
    try {
        # Construct path safely
        $SafeFile = $File -replace "/", "\"
        $LocalPath = Join-Path $OutputDir $SafeFile
        
        # Determine parent directory
        $ParentDir = Split-Path -Path $LocalPath -Parent
        if (-not $ParentDir) {
            throw "Could not determine parent directory for $LocalPath"
        }
        
        if (!(Test-Path $ParentDir)) {
            New-Item -ItemType Directory -Force -Path $ParentDir | Out-Null
        }

        $Url = "$BaseUrl/$File"
        Write-Host "Downloading $File..." -NoNewline

        # Robust Method: System.Net.WebClient
        # Avoids Invoke-WebRequest "IE" dependency and BITS service issues
        try {
            $WebClient = New-Object System.Net.WebClient
            $WebClient.DownloadFile($Url, $LocalPath)
            $WebClient.Dispose()
            Write-Host " [OK]" -ForegroundColor Green
        }
        catch {
            # Check for 404 and try fallback if it looks like an fp16 file
            $Is404 = $_.Exception.InnerException.Response.StatusCode -eq [System.Net.HttpStatusCode]::NotFound
            if ($Is404 -and $File -match "\.fp16\.safetensors$") {
                $FallbackFile = $File -replace "\.fp16\.safetensors$", ".safetensors"
                $FallbackUrl = "$BaseUrl/$FallbackFile"
                $LocalPathFallback = $LocalPath -replace "\.fp16\.safetensors$", ".safetensors"
                  
                Write-Host "`n  404 on FP16. Retrying with fallback: $FallbackFile..." -NoNewline -ForegroundColor Yellow
                  
                try {
                    $WebClient = New-Object System.Net.WebClient
                    $WebClient.DownloadFile($FallbackUrl, $LocalPathFallback)
                    $WebClient.Dispose()
                    Write-Host " [OK]" -ForegroundColor Green
                    continue
                }
                catch {
                    Write-Host " [FAILED FALLBACK]" -ForegroundColor Red
                    Write-Host "Error: $_" -ForegroundColor Red
                    exit 1
                }
            }

            Write-Host " [FAILED]" -ForegroundColor Red
            Write-Host "Error: $_" -ForegroundColor Red
            exit 1
        }
    }
    catch {
        Write-Host " [FATAL ERROR]" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nDownload Complete!" -ForegroundColor Green
Write-Host "Model valid at: $OutputDir"
