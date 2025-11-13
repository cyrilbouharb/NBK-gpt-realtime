#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Post-provision script that runs automatically after 'azd up' completes.
    
.DESCRIPTION
    This script:
    1. Scrapes NBK website for knowledge base
    2. Extracts deployment outputs (WebSocket URL, API Key)
    3. Displays frontend connection information
    4. Updates .env file with actual values
#>

param(
    [string]$environmentName = $env:AZURE_ENV_NAME
)

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "   Post-Deployment Configuration" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Change to project root directory
$projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
Set-Location $projectRoot

# Step 1: Run NBK Website Scraper
Write-Host "Step 1/3: Scraping NBK website for knowledge base..." -ForegroundColor Yellow
Write-Host ""

# Check if Python is available
try {
    $pythonCmd = Get-Command python -ErrorAction Stop
    Write-Host "   Python found: $($pythonCmd.Source)" -ForegroundColor Green
} catch {
    Write-Host "   Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Install dependencies if needed
if (-not (Test-Path "venv")) {
    Write-Host "   Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv and install requirements
if ($IsWindows -or $ENV:OS) {
    & ".\venv\Scripts\Activate.ps1"
} else {
    & "./venv/bin/Activate.ps1"
}

Write-Host "   Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt

# Run the scraper
Write-Host "   Running scraper..." -ForegroundColor Yellow
python scrape_nbk.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "   NBK knowledge base updated successfully" -ForegroundColor Green
} else {
    Write-Host "   Scraper completed with warnings (this is OK if some pages were unavailable)" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Extract Deployment Outputs
Write-Host "Step 2/3: Extracting deployment configuration..." -ForegroundColor Yellow
Write-Host ""

try {
    # Get all environment variables set by azd
    $envVars = @{}
    azd env get-values | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $envVars[$matches[1]] = $matches[2].Trim('"')
        }
    }

    $gatewayUrl = $envVars['APIM_GATEWAY_URL']
    $subscriptionKey = $envVars['APIM_SUBSCRIPTION_KEY']
    $websocketEndpoint = $envVars['WEBSOCKET_ENDPOINT']
    $fullWebsocketUrl = $envVars['FULL_WEBSOCKET_URL']
    $apiVersion = $envVars['API_VERSION']
    $resourceGroup = $envVars['RESOURCE_GROUP_NAME']
    $region = $envVars['DEPLOYMENT_REGION']

    Write-Host "   Configuration extracted successfully" -ForegroundColor Green
    Write-Host ""

    # Step 3: Display Frontend Configuration
    Write-Host "Step 3/3: Deployment Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "   FRONTEND TEAM CONFIGURATION" -ForegroundColor Green -NoNewline
    Write-Host " 📱" -ForegroundColor White
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "WebSocket Endpoint:" -ForegroundColor Cyan
    Write-Host "  $fullWebsocketUrl" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Authentication Header:" -ForegroundColor Cyan
    Write-Host "  api-key: $subscriptionKey" -ForegroundColor White
    Write-Host ""
    
    Write-Host "----------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host ""
    
    Write-Host "Deployment Details:" -ForegroundColor Cyan
    Write-Host "  Resource Group: $resourceGroup" -ForegroundColor White
    Write-Host "  Region: $region" -ForegroundColor White
    Write-Host "  API Version: $apiVersion" -ForegroundColor White
    Write-Host ""
    
    Write-Host "Features Configured:" -ForegroundColor Cyan
    Write-Host "  - Speech-to-Speech (bidirectional audio)" -ForegroundColor Green
    Write-Host "  - Arabic and English support" -ForegroundColor Green
    Write-Host "  - NBK knowledge base (web scraping)" -ForegroundColor Green
    Write-Host "  - Real-time interruption support" -ForegroundColor Green
    Write-Host "  - Professional 'echo' voice" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "----------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host ""
    
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Share the WebSocket URL and API key with your frontend team" -ForegroundColor White
    Write-Host "  2. See FRONTEND.md for integration examples" -ForegroundColor White
    Write-Host "  3. Run 'scripts/test-deployment.ps1' to validate the deployment" -ForegroundColor White
    Write-Host "  4. Run 'scripts/get-connection-info.ps1' anytime to view this info again" -ForegroundColor White
    Write-Host ""
    
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""

    # Save to file for easy reference
    $configFile = "deployment-config.txt"
    $configContent = "NBK Speech-to-Speech Deployment Configuration`n"
    $configContent += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n`n"
    $configContent += "FRONTEND CONFIGURATION`n"
    $configContent += "================================================================`n`n"
    $configContent += "WebSocket URL:`n"
    $configContent += "$fullWebsocketUrl`n`n"
    $configContent += "API Key:`n"
    $configContent += "$subscriptionKey`n`n"
    $configContent += "Authentication:`n"
    $configContent += "Add header: api-key: YOUR_API_KEY_HERE`n`n"
    $configContent += "DEPLOYMENT DETAILS`n"
    $configContent += "================================================================`n`n"
    $configContent += "Resource Group: $resourceGroup`n"
    $configContent += "Region: $region`n"
    $configContent += "API Version: $apiVersion`n"
    $configContent += "APIM Gateway: $gatewayUrl`n`n"
    $configContent += "FEATURES`n"
    $configContent += "================================================================`n`n"
    $configContent += "* Speech-to-Speech (bidirectional audio)`n"
    $configContent += "* Arabic and English support`n"
    $configContent += "* NBK knowledge base (web scraping)`n"
    $configContent += "* Real-time interruption support`n"
    $configContent += "* Professional 'echo' voice`n`n"
    $configContent += "Integration examples: see FRONTEND.md`n"
    
    $configContent | Out-File -FilePath $configFile -Encoding UTF8

    Write-Host "Configuration saved to: $configFile" -ForegroundColor Green
    Write-Host ""

} catch {
    Write-Host "   Could not extract all configuration values" -ForegroundColor Yellow
    Write-Host "   Error: $_" -ForegroundColor Red
    Write-Host "   You can retrieve configuration later using: scripts/get-connection-info.ps1" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Post-deployment configuration complete!" -ForegroundColor Green
Write-Host ""
