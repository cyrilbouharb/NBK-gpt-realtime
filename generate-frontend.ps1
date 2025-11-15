# Generate production-ready frontend HTML with connection details from .env
# Run this after 'azd up' to create a ready-to-use frontend

Write-Host "Generating frontend with deployment configuration..." -ForegroundColor Cyan

# Load .env file
$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "ERROR: .env file not found. Please run 'azd up' first." -ForegroundColor Red
    exit 1
}

# Parse .env
$envVars = @{}
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
    }
}

# Extract required values
$wsUrl = $envVars['FULL_WEBSOCKET_URL']
$apiKey = $envVars['APIM_SUBSCRIPTION_KEY']
$apimGateway = $envVars['APIM_GATEWAY_URL']

if (-not $wsUrl -or -not $apiKey) {
    Write-Host "ERROR: Missing required environment variables in .env" -ForegroundColor Red
    Write-Host "   FULL_WEBSOCKET_URL: $wsUrl" -ForegroundColor Yellow
    Write-Host "   APIM_SUBSCRIPTION_KEY: $apiKey" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found configuration:" -ForegroundColor Green
Write-Host "   WebSocket URL: $wsUrl" -ForegroundColor White
Write-Host "   API Key: $($apiKey.Substring(0, [Math]::Min(20, $apiKey.Length)))..." -ForegroundColor White

# Read template
$templateFile = Join-Path $PSScriptRoot "test-ui.html"
$template = Get-Content $templateFile -Raw

# Replace placeholders
$output = $template -replace 'value=""(\s+placeholder="wss://your-apim.*?")', "value=`"$wsUrl`"`$1"
$output = $output -replace '(id="apiKey"[^>]*value=")("[^>]*placeholder="Your APIM subscription key")', "`$1$apiKey`$2"

# Save to nbk-frontend.html
$outputFile = Join-Path $PSScriptRoot "nbk-frontend.html"
$output | Set-Content $outputFile -Encoding UTF8

Write-Host "SUCCESS: Frontend generated at nbk-frontend.html" -ForegroundColor Green
Write-Host ""
Write-Host "Deployment Summary:" -ForegroundColor Cyan
Write-Host "   APIM Gateway: $apimGateway" -ForegroundColor White
Write-Host "   WebSocket Endpoint: $wsUrl" -ForegroundColor White
Write-Host "   Authentication: API Key (via query parameter)" -ForegroundColor White
Write-Host "   Voice: Echo (Professional Male - configured on backend)" -ForegroundColor White
Write-Host "   System Prompt: Configured on backend with NBK knowledge" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open nbk-frontend.html in a browser" -ForegroundColor White
Write-Host "   2. Click Connect to establish WebSocket connection" -ForegroundColor White
Write-Host "   3. Hold the microphone button and speak" -ForegroundColor White
Write-Host "   4. Share nbk-frontend.html with your frontend team" -ForegroundColor White
Write-Host ""
Write-Host "Security Note:" -ForegroundColor Yellow
Write-Host "   The generated HTML contains the API key for testing." -ForegroundColor White
Write-Host "   For production, implement proper key management." -ForegroundColor White
