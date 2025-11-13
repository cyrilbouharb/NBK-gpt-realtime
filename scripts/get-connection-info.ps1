#Requires -Version 5.1
<#
.SYNOPSIS
    Displays NBK Realtime API connection information

.DESCRIPTION
    Retrieves and displays the WebSocket URL and API key from the azd environment.
    Useful for sharing connection details with frontend teams.
    
    Run this anytime after 'azd up' to get the connection information.
#>

param(
    [switch]$CopyToClipboard,
    [switch]$SaveToFile
)

$ErrorActionPreference = "Stop"

# Check if azd environment exists
try {
    $null = azd env list 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ No azd environment found" -ForegroundColor Red
        Write-Host "   Run 'azd up' first to deploy the infrastructure" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host "❌ Error checking azd environment: $_" -ForegroundColor Red
    exit 1
}

# Extract outputs from azd environment
Write-Host "`nRetrieving deployment information..." -ForegroundColor Cyan

try {
    $envVars = azd env get-values | Out-String
    
    # Parse environment variables
    $apimGatewayUrl = ($envVars | Select-String 'APIM_GATEWAY_URL="([^"]+)"').Matches.Groups[1].Value
    $apimSubscriptionKey = ($envVars | Select-String 'APIM_SUBSCRIPTION_KEY="([^"]+)"').Matches.Groups[1].Value
    $apimSubscriptionName = ($envVars | Select-String 'APIM_SUBSCRIPTION_NAME="([^"]+)"').Matches.Groups[1].Value
    $websocketEndpoint = ($envVars | Select-String 'WEBSOCKET_ENDPOINT="([^"]+)"').Matches.Groups[1].Value
    $fullWebsocketUrl = ($envVars | Select-String 'FULL_WEBSOCKET_URL="([^"]+)"').Matches.Groups[1].Value
    $apiVersion = ($envVars | Select-String 'API_VERSION="([^"]+)"').Matches.Groups[1].Value
    $resourceGroup = ($envVars | Select-String 'RESOURCE_GROUP_NAME="([^"]+)"').Matches.Groups[1].Value
    $region = ($envVars | Select-String 'DEPLOYMENT_REGION="([^"]+)"').Matches.Groups[1].Value
    
    if (-not $fullWebsocketUrl -or -not $apimSubscriptionKey) {
        Write-Host "❌ Could not extract connection information" -ForegroundColor Red
        Write-Host "   Make sure the deployment completed successfully" -ForegroundColor Yellow
        exit 1
    }
}
catch {
    Write-Host "❌ Error extracting connection information: $_" -ForegroundColor Red
    exit 1
}

# Display connection information
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "NBK Realtime API - Connection Info" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "WebSocket URL:" -ForegroundColor White
Write-Host "  $fullWebsocketUrl" -ForegroundColor Green

Write-Host "`nAPI Key (Subscription):" -ForegroundColor White
Write-Host "  $apimSubscriptionKey" -ForegroundColor Green

Write-Host "`nAuthentication Header:" -ForegroundColor White
Write-Host "  api-key: $apimSubscriptionKey" -ForegroundColor Yellow

Write-Host "`nDeployment Details:" -ForegroundColor White
Write-Host "  Resource Group: $resourceGroup" -ForegroundColor Gray
Write-Host "  Region: $region" -ForegroundColor Gray
Write-Host "  API Version: $apiVersion" -ForegroundColor Gray
Write-Host "  Subscription Name: $apimSubscriptionName" -ForegroundColor Gray

Write-Host "`nFeatures:" -ForegroundColor White
Write-Host "  ✅ Real-time Speech-to-Speech" -ForegroundColor Green
Write-Host "  ✅ Arabic Language Support" -ForegroundColor Green
Write-Host "  ✅ NBK Knowledge Base Grounding" -ForegroundColor Green
Write-Host "  ✅ Interruption Handling" -ForegroundColor Green
Write-Host "  ✅ Voice: Echo (Professional Banking)" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "For Frontend Teams:" -ForegroundColor White
Write-Host "  1. Use the WebSocket URL and API key above" -ForegroundColor Yellow
Write-Host "  2. See FRONTEND.md for integration examples" -ForegroundColor Yellow
Write-Host "  3. Test connection: python examples\test-client.py" -ForegroundColor Yellow

Write-Host "`nFor Validation:" -ForegroundColor White
Write-Host "  Run: .\scripts\test-deployment.ps1" -ForegroundColor Cyan

Write-Host ""

# Copy to clipboard if requested
if ($CopyToClipboard) {
    $clipboardText = @"
NBK Realtime API Connection Info
================================

WebSocket URL: $fullWebsocketUrl
API Key: $apimSubscriptionKey
Authentication: api-key: $apimSubscriptionKey

Resource Group: $resourceGroup
Region: $region
API Version: $apiVersion
"@
    
    $clipboardText | Set-Clipboard
    Write-Host "✅ Connection information copied to clipboard!" -ForegroundColor Green
}

# Save to file if requested
if ($SaveToFile) {
    $outputPath = Join-Path $PSScriptRoot "..\connection-info.txt"
    
    $fileContent = @"
NBK Realtime API - Connection Information
=========================================

WebSocket URL:
  $fullWebsocketUrl

API Key (Subscription):
  $apimSubscriptionKey

Authentication Header:
  api-key: $apimSubscriptionKey

Deployment Details:
  Resource Group: $resourceGroup
  Region: $region
  API Version: $apiVersion
  Subscription Name: $apimSubscriptionName

Features:
  - Real-time Speech-to-Speech
  - Arabic Language Support
  - NBK Knowledge Base Grounding
  - Interruption Handling
  - Voice: Echo (Professional Banking)

Frontend Integration:
  See FRONTEND.md for code examples in JavaScript, Python, and C#

Testing:
  Run: python examples\test-client.py
  Validate: .\scripts\test-deployment.ps1

Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@
    
    $fileContent | Set-Content $outputPath -Encoding UTF8
    Write-Host "✅ Connection information saved to: $outputPath" -ForegroundColor Green
}

Write-Host ""
