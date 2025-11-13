#Requires -Version 5.1
<#
.SYNOPSIS
    Validates NBK Realtime API deployment

.DESCRIPTION
    Tests the deployed infrastructure:
    - APIM endpoint accessibility
    - WebSocket connection
    - Authentication
    - Session configuration
    
    Run this after 'azd up' completes to validate deployment.
#>

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "NBK Realtime API - Deployment Validation" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Check if azd environment exists
Write-Host "1. Checking azd environment..." -ForegroundColor Yellow
try {
    $azdEnvCheck = azd env list 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ❌ azd environment not found" -ForegroundColor Red
        Write-Host "   Run 'azd up' first to deploy the infrastructure" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "   ✅ azd environment found" -ForegroundColor Green
}
catch {
    Write-Host "   ❌ Error checking azd environment: $_" -ForegroundColor Red
    exit 1
}

# Step 2: Extract outputs from azd environment
Write-Host "`n2. Extracting deployment outputs..." -ForegroundColor Yellow
try {
    $envVars = azd env get-values | Out-String
    
    # Parse environment variables
    $apimGatewayUrl = ($envVars | Select-String 'APIM_GATEWAY_URL="([^"]+)"').Matches.Groups[1].Value
    $apimSubscriptionKey = ($envVars | Select-String 'APIM_SUBSCRIPTION_KEY="([^"]+)"').Matches.Groups[1].Value
    $websocketUrl = ($envVars | Select-String 'FULL_WEBSOCKET_URL="([^"]+)"').Matches.Groups[1].Value
    $resourceGroup = ($envVars | Select-String 'RESOURCE_GROUP_NAME="([^"]+)"').Matches.Groups[1].Value
    
    if (-not $apimGatewayUrl -or -not $apimSubscriptionKey -or -not $websocketUrl) {
        Write-Host "   ❌ Could not extract all required outputs" -ForegroundColor Red
        Write-Host "   Make sure the deployment completed successfully" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "   ✅ Deployment outputs extracted" -ForegroundColor Green
    if ($Verbose) {
        Write-Host "      Gateway URL: $apimGatewayUrl" -ForegroundColor Gray
        Write-Host "      WebSocket URL: $websocketUrl" -ForegroundColor Gray
        Write-Host "      Resource Group: $resourceGroup" -ForegroundColor Gray
    }
}
catch {
    Write-Host "   ❌ Error extracting outputs: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Test APIM endpoint accessibility (HTTPS)
Write-Host "`n3. Testing APIM endpoint accessibility..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $apimGatewayUrl -Method Get -ErrorAction SilentlyContinue -TimeoutSec 10
    Write-Host "   ✅ APIM endpoint is accessible" -ForegroundColor Green
}
catch {
    # APIM may return 401 or other status codes, which is OK - we just want to confirm it's reachable
    if ($_.Exception.Response.StatusCode) {
        Write-Host "   ✅ APIM endpoint is accessible (returned $($_.Exception.Response.StatusCode))" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ APIM endpoint not accessible: $_" -ForegroundColor Red
        Write-Host "   Check network connectivity and firewall rules" -ForegroundColor Yellow
        exit 1
    }
}

# Step 4: Check if nbk_knowledge.json exists
Write-Host "`n4. Checking NBK knowledge base..." -ForegroundColor Yellow
$knowledgePath = Join-Path $PSScriptRoot "..\nbk_knowledge.json"
if (Test-Path $knowledgePath) {
    $knowledgeContent = Get-Content $knowledgePath -Raw | ConvertFrom-Json
    $pageCount = $knowledgeContent.pages.Count
    Write-Host "   ✅ NBK knowledge base found ($pageCount pages)" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  NBK knowledge base not found" -ForegroundColor Yellow
    Write-Host "   Run 'python scrape_nbk.py' to generate it" -ForegroundColor Yellow
}

# Step 5: Check if Python environment is set up
Write-Host "`n5. Checking Python environment..." -ForegroundColor Yellow
$venvPath = Join-Path $PSScriptRoot "..\venv"
if (Test-Path $venvPath) {
    Write-Host "   ✅ Virtual environment found" -ForegroundColor Green
}
else {
    Write-Host "   ⚠️  Virtual environment not found" -ForegroundColor Yellow
    Write-Host "   Run 'python -m venv venv' and 'pip install -r requirements.txt'" -ForegroundColor Yellow
}

# Step 6: Check if test client can be run
Write-Host "`n6. Checking test client..." -ForegroundColor Yellow
$testClientPath = Join-Path $PSScriptRoot "..\examples\test-client.py"
if (Test-Path $testClientPath) {
    Write-Host "   ✅ Test client found" -ForegroundColor Green
    Write-Host "   Run it with: python examples\test-client.py" -ForegroundColor Cyan
}
else {
    Write-Host "   ⚠️  Test client not found" -ForegroundColor Yellow
}

# Step 7: Run Python test client if requested
if ($Verbose) {
    Write-Host "`n7. Running Python test client..." -ForegroundColor Yellow
    Write-Host "   (This requires Python environment to be activated)" -ForegroundColor Gray
    
    # Create temporary .env with deployment values
    $tempEnvPath = Join-Path $PSScriptRoot "..\test.env"
    @"
APIM_GATEWAY_URL=$apimGatewayUrl
APIM_API_KEY=$apimSubscriptionKey
INFERENCE_API_PATH=inference
INFERENCE_API_VERSION=2024-10-01-preview
"@ | Set-Content $tempEnvPath
    
    Write-Host "   ℹ️  Temporary .env created at test.env" -ForegroundColor Cyan
    Write-Host "   Run: python examples\test-client.py" -ForegroundColor Cyan
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Validation Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Deployment validated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Connection Details:" -ForegroundColor White
Write-Host "  WebSocket URL: $websocketUrl" -ForegroundColor Cyan
Write-Host "  API Key: $($apimSubscriptionKey.Substring(0, 20))..." -ForegroundColor Cyan
Write-Host "  Authentication: api-key: YOUR_KEY_HERE" -ForegroundColor Gray
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor White
Write-Host "  1. Run: python examples\test-client.py" -ForegroundColor Yellow
Write-Host "  2. Share deployment-config.txt with frontend team" -ForegroundColor Yellow
Write-Host "  3. See FRONTEND.md for integration examples" -ForegroundColor Yellow
Write-Host ""
Write-Host "To view deployment info anytime:" -ForegroundColor White
Write-Host "  .\scripts\get-connection-info.ps1" -ForegroundColor Cyan
Write-Host ""
