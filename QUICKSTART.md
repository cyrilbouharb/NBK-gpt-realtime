# NBK Voice Assistant - Quick Start

Deploy NBK Realtime Voice Assistant to Azure in 3 commands.

## Prerequisites

- Azure subscription
- Azure Portal Cloud Shell (or Azure CLI installed locally)

## Quick Deployment

### Option 1: Cloud Shell (Recommended)

1. Open [Azure Portal](https://portal.azure.com)
2. Click Cloud Shell icon (>_) and choose Bash
3. Run these commands:

```bash
# Clone the repository
git clone https://github.com/cyrilbouharb/NBK-gpt-realtime.git
cd NBK-gpt-realtime

# Run deployment script (uses only az commands, no Docker/azd needed!)
chmod +x deploy.sh
./deploy.sh
```

**That's it!** The script will:
- ✅ Create resource group
- ✅ Deploy Azure OpenAI, APIM, Container Registry, Container App
- ✅ Build Docker image in Azure (no local Docker needed!)
- ✅ Deploy backend
- ✅ Show your WebSocket URL and API key

**Deployment time**: ~8-12 minutes

### Option 2: Update Backend Only

After initial deployment, to update just the backend code:

```bash
cd NBK-gpt-realtime

# Run update script
./update-backend.sh
```

## Get Your WebSocket URL

After deployment, the script displays:

```
Complete WebSocket URL:
wss://apim-abc123.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime&api-key=YOUR-KEY
```

Use this URL in your frontend application.

## Test the Deployment

```bash
# Check backend health
BACKEND_URL=$(az deployment group show -g rg-nbk-voice -n main --query properties.outputs.BACKEND_URL.value -o tsv)
curl $BACKEND_URL/health
```

Expected response:
```json
{
  "status": "healthy",
  "knowledge_entries": 3,
  "instructions_length": 2211
}
```

## Clean Up

To delete all resources:

```bash
az group delete --name rg-nbk-voice --yes --no-wait
```

## Troubleshooting

If deployment fails:
1. Check you're logged into the correct Azure subscription: `az account show`
2. Verify you have permissions to create resources
3. Review error messages in deployment output

## What Gets Deployed?

- **Azure OpenAI** - GPT-4o Realtime model (10 TPM)
- **APIM** - API Management for secure endpoint
- **Container Registry** - Stores backend Docker image
- **Container App** - Runs FastAPI WebSocket proxy
- **Application Insights** - Monitoring and logs
- **Log Analytics** - Centralized logging

**Estimated monthly cost**: ~$95-135 (excluding Azure OpenAI usage)

## Documentation

For detailed documentation, see [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
