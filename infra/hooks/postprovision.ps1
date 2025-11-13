#!/usr/bin/env pwsh
# Post-provision hook for NBK Speech-to-Speech deployment
# Runs automatically after 'azd up' or 'azd provision'

param([string]$environmentName = $env:AZURE_ENV_NAME)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "================================================================"
Write-Host "   Post-Deployment Configuration"
Write-Host "================================================================"
Write-Host ""

# Change to project root
$projectRoot = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSCommandPath))
Set-Location $projectRoot

# Step 1: Run scraper
Write-Host "Step 1/3: Scraping NBK website..." -ForegroundColor Yellow
Write-Host ""

try {
    $pythonCmd = Get-Command python -ErrorAction Stop
    Write-Host "   Python found" -ForegroundColor Green
} catch {
    Write-Host "   ERROR: Python not found" -ForegroundColor Red
    exit 1
}

# Create venv if needed
if (-not (Test-Path "venv")) {
    Write-Host "   Creating virtual environment..."
    python -m venv venv
}

# Activate venv
if ($IsWindows -or $ENV:OS) {
    & ".\venv\Scripts\Activate.ps1"
} else {
    & "./venv/bin/Activate.ps1"
}

Write-Host "   Installing dependencies..."
pip install -q -r requirements.txt

Write-Host "   Running scraper..."
python scrape_nbk.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "   Knowledge base updated" -ForegroundColor Green
} else {
    Write-Host "   Scraper completed with warnings" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Extract deployment outputs
Write-Host "Step 2/3: Extracting configuration..." -ForegroundColor Yellow
Write-Host ""

try {
    $envVars = @{}
    azd env get-values | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $envVars[$matches[1]] = $matches[2].Trim('"')
        }
    }

    $gatewayUrl = $envVars['APIM_GATEWAY_URL']
    $subscriptionKey = $envVars['APIM_SUBSCRIPTION_KEY']
    $fullWebsocketUrl = $envVars['FULL_WEBSOCKET_URL']
    $apiVersion = $envVars['API_VERSION']
    $resourceGroup = $envVars['RESOURCE_GROUP_NAME']
    $region = $envVars['DEPLOYMENT_REGION']

    Write-Host "   Configuration extracted" -ForegroundColor Green
    Write-Host ""

    # Step 3: Display configuration
    Write-Host "Step 3/3: Deployment Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "================================================================"
    Write-Host "   FRONTEND CONFIGURATION"
    Write-Host "================================================================"
    Write-Host ""
    
    Write-Host "WebSocket Endpoint:" -ForegroundColor Cyan
    Write-Host "  $fullWebsocketUrl"
    Write-Host ""
    
    Write-Host "Authentication Header:" -ForegroundColor Cyan
    Write-Host "  api-key: $subscriptionKey"
    Write-Host ""
    
    Write-Host "Deployment Details:" -ForegroundColor Cyan
    Write-Host "  Resource Group: $resourceGroup"
    Write-Host "  Region: $region"
    Write-Host "  API Version: $apiVersion"
    Write-Host ""
    
    Write-Host "Features:" -ForegroundColor Cyan
    Write-Host "  - Speech-to-Speech (bidirectional audio)"
    Write-Host "  - Arabic and English support"
    Write-Host "  - NBK knowledge base"
    Write-Host "  - Real-time interruption"
    Write-Host "  - Professional echo voice"
    Write-Host ""
    
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "  1. Share WebSocket URL and API key with frontend team"
    Write-Host "  2. See FRONTEND.md for integration examples"
    Write-Host "  3. Run scripts\test-deployment.ps1 to validate"
    Write-Host ""
    Write-Host "================================================================"
    Write-Host ""

    # Save to file
    $configFile = "deployment-config.txt"
    $lines = @(
        "NBK Speech-to-Speech Deployment Configuration",
        "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
        "",
        "FRONTEND CONFIGURATION",
        "================================================================",
        "",
        "WebSocket URL:",
        $fullWebsocketUrl,
        "",
        "API Key:",
        $subscriptionKey,
        "",
        "Authentication:",
        "Add header: api-key: YOUR_API_KEY_HERE",
        "",
        "DEPLOYMENT DETAILS",
        "================================================================",
        "",
        "Resource Group: $resourceGroup",
        "Region: $region",
        "API Version: $apiVersion",
        "APIM Gateway: $gatewayUrl",
        "",
        "FEATURES",
        "================================================================",
        "",
        "* Speech-to-Speech (bidirectional audio)",
        "* Arabic and English support",
        "* NBK knowledge base (web scraping)",
        "* Real-time interruption support",
        "* Professional echo voice",
        "",
        "Integration examples: see FRONTEND.md"
    )
    
    $lines | Out-File -FilePath $configFile -Encoding UTF8

    Write-Host "Configuration saved to: $configFile" -ForegroundColor Green
    Write-Host ""

} catch {
    Write-Host "   Could not extract configuration" -ForegroundColor Yellow
    Write-Host "   Error: $_" -ForegroundColor Red
    Write-Host "   Run scripts\get-connection-info.ps1 later" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Post-deployment complete!" -ForegroundColor Green
Write-Host ""
