# NBK Realtime Voice Assistant - Deployment Guide

This guide provides step-by-step instructions to deploy the NBK Realtime Voice Assistant infrastructure to Azure using Azure Developer CLI (azd).

## Architecture Overview

The solution consists of:
- **Azure OpenAI Realtime API** - GPT-4o Realtime model for speech-to-speech conversations
- **FastAPI Backend (Container App)** - WebSocket proxy that injects NBK knowledge into conversations
- **Azure Container Registry** - Stores the backend Docker image
- **Azure API Management** - Provides secure endpoint with subscription key authentication
- **Application Insights & Log Analytics** - Monitoring and diagnostics

## Prerequisites

### Choose Your Deployment Method

You have **TWO options**. Choose ONE:

---

### ✅ OPTION 1: Azure Cloud Shell (RECOMMENDED - No local setup!)

**Use this if you're on a new laptop or don't want to install anything locally.**

1. Go to [Azure Portal](https://portal.azure.com)
2. Click the **Cloud Shell icon (>_)** in the top navigation bar
3. Choose **Bash** (recommended)
4. Clone the repository:
   ```bash
   git clone https://github.com/cyrilbouharb/NBK-gpt-realtime.git
   cd NBK-gpt-realtime
   ```
5. Install Azure Developer CLI:
   ```bash
   curl -fsSL https://aka.ms/install-azd.sh | bash
   ```
6. **Docker is already installed in Cloud Shell** - you're ready to go!
7. Skip to "Deployment Steps" section below

---

### ✅ OPTION 2: Local Deployment (Mac/Windows/Linux)

**Use this if you want to deploy from your local machine.**

**Required tools:**
1. **Azure Subscription** with permissions to create resources
2. **Azure Developer CLI (azd)** - [Install azd](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
3. **Docker Desktop** - [Install Docker](https://www.docker.com/products/docker-desktop/)
   - **Mac**: Install Docker Desktop for Mac and start it (whale icon in menu bar should be stable)
   - **Windows**: Install Docker Desktop for Windows and start it
   - **Verify Docker is running**: `docker ps` (should show container list, not error)
4. **Git** to clone the repository

**Setup steps:**
```bash
# Clone the repo
git clone https://github.com/cyrilbouharb/NBK-gpt-realtime.git
cd NBK-gpt-realtime

# Verify Docker is running
docker ps
# Should show: CONTAINER ID   IMAGE   ... (or empty list)
# Should NOT show: "Cannot connect to Docker daemon"
```

---

## Deployment Steps

### 1. Clone or Navigate to the Project

```powershell
cd "C:\Users\<your-user>\POCs\S2S Realtime NBK"
```

### 2. Login to Azure

```bash
azd auth login
```

This will open a browser window for Azure authentication.

### 3. Initialize the Azure Environment

```bash
azd init
```

When prompted:
- **Environment name**: Choose a name (e.g., `nbk-voice-prod`)
- **Azure subscription**: Select your target subscription
- **Azure location**: Select your preferred region (e.g., `swedencentral`)

### 4. Set Required Parameters

Edit `main.parameters.json` or set via azd environment variables:

```bash
azd env set AZURE_LOCATION "swedencentral"
```

### 5. Deploy Infrastructure and Application

```bash
azd up
```

This command will:
1. Provision all Azure resources (APIM, Azure OpenAI, Container Registry, Container App Environment)
2. Build the Docker image for the backend
3. Push the image to Azure Container Registry
4. Deploy the Container App with the backend service
5. Configure APIM to route to the backend
6. Run the post-provision hook to scrape NBK knowledge

**Expected deployment time**: 15-20 minutes

### 6. Retrieve Connection Information

After deployment completes, get the connection details:

```bash
azd env get-values
```

Key outputs you'll need:
- `APIM_GATEWAY_URL` - API Management gateway URL
- `APIM_SUBSCRIPTION_KEY` - Subscription key for authentication
- `WEBSOCKET_ENDPOINT` - Full WebSocket endpoint URL
- `AZURE_CONTAINER_REGISTRY_NAME` - Container registry name
- `AZURE_CONTAINER_APP_NAME` - Container App name

### 7. Get Your Frontend Connection URL

After deployment, retrieve your WebSocket endpoint and API key:

**Step 1: Get the APIM Gateway URL and Subscription Key**

```bash
# Get all deployment outputs
azd env get-values

# Or get specific values (PowerShell)
azd env get-values | Select-String "APIM_GATEWAY_URL"
azd env get-values | Select-String "APIM_SUBSCRIPTION_KEY"

# For Linux/Mac (bash)
azd env get-values | grep "APIM_GATEWAY_URL"
azd env get-values | grep "APIM_SUBSCRIPTION_KEY"
```

**Example output**:
```
APIM_GATEWAY_URL="https://apim-abc123.azure-api.net"
APIM_SUBSCRIPTION_KEY="c85b42ae7ec14a60b1eb8bd38d4b4116"
```

**Step 2: Build your complete WebSocket URL**

Format:
```
wss://<APIM_GATEWAY_URL>/inference/openai/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime&api-key=<APIM_SUBSCRIPTION_KEY>
```

**Example with values from above**:
```
wss://apim-abc123.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime&api-key=c85b42ae7ec14a60b1eb8bd38d4b4116
```

**Quick method**: You can also get the pre-built URL:
```bash
azd env get-values | Select-String "FULL_WEBSOCKET_URL"
# Output: FULL_WEBSOCKET_URL="wss://apim-abc123.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime"

# Then append the API key
# Final URL: <FULL_WEBSOCKET_URL>&api-key=<APIM_SUBSCRIPTION_KEY>
```

## Testing the Deployment

### Option 1: Use the Test Frontend (Browser)

1. Open `test-frontend-vad.html` in a browser
2. Update the WebSocket URL and API key in the file (lines 195-196)
3. Click "Connect" then "Start Talking"
4. Speak naturally - the system uses server-side Voice Activity Detection

### Option 2: Test via Azure Portal

1. Go to Azure Portal → Your Resource Group
2. Open the Container App (`ca-nbk-backend-<suffix>`)
3. Click "Log stream" to see live logs
4. Connect from your frontend and watch the logs for connection events

### Option 3: Check Backend Health

```bash
curl https://<BACKEND_FQDN>/health
```

Expected response:
```json
{
  "status": "healthy",
  "knowledge_entries": 3,
  "instructions_length": 2211
}
```

## Post-Deployment Configuration

### Updating NBK Knowledge Base

The NBK knowledge is stored in `nbk_knowledge.json`. To update it:

1. Edit `scrape_nbk.py` to add/modify URLs
2. Run the scraper:
   ```bash
   python scrape_nbk.py
   ```
3. Redeploy the backend:
   ```bash
   # Option A: Use Docker (recommended - azd deploy has known bugs)
   docker buildx build --platform linux/amd64 -t <ACR_NAME>.azurecr.io/backend:latest --push .
   az containerapp update --name <CONTAINER_APP_NAME> --resource-group <RG> --image <ACR_NAME>.azurecr.io/backend:latest

   # Option B: Try azd deploy (may fail with "containerAppName cannot be empty")
   azd deploy backend
   ```

**Note**: `azd deploy` currently has a bug where it may fail. Use the Docker commands above as a workaround.

### Adjusting Voice Activity Detection (VAD) Settings

Edit `backend/main.py`, lines 134-138:

```python
"turn_detection": {
    "type": "server_vad",
    "threshold": 0.5,           # Lower = more sensitive (0.0 - 1.0)
    "prefix_padding_ms": 300,   # Audio captured before speech
    "silence_duration_ms": 500  # Silence before considering speech ended
}
```

Then redeploy:
```bash
azd deploy backend
```

### Changing the Voice

Edit `backend/main.py`, line 131:

```python
"voice": "echo"  # Options: alloy, ash, ballad, coral, echo, sage, shimmer, verse
```

### Scaling the Container App

To handle more concurrent users, adjust in `modules/containerapp.bicep`:

```bicep
scale: {
  minReplicas: 1   // Minimum instances
  maxReplicas: 10  // Maximum instances
}
```

Then run `azd up` to apply changes.

## Monitoring and Logs

### View Container App Logs

```bash
az containerapp logs show \
  --name <AZURE_CONTAINER_APP_NAME> \
  --resource-group <RESOURCE_GROUP_NAME> \
  --tail 50 --follow
```

### View Application Insights

1. Azure Portal → Your Resource Group
2. Open Application Insights resource
3. Navigate to "Logs" or "Live Metrics"

### Check APIM Analytics

1. Azure Portal → Your Resource Group
2. Open API Management resource
3. Navigate to "Analytics" to see API usage metrics

## Troubleshooting

### Issue: "Docker daemon is not running" error during `azd up`

**Error message**: `error checking for external tool Docker daemon is not running`

**Solutions**:

**Option A: Start Docker Desktop**
1. Open Docker Desktop application
2. Wait for it to fully start (whale icon should be stable)
3. Verify: `docker ps` should show no errors
4. Run `azd up` again

**Option B: Use Azure Cloud Shell (Recommended for new laptops)**
1. Go to [Azure Portal](https://portal.azure.com)
2. Click Cloud Shell icon (>_) at top
3. Choose Bash or PowerShell
4. Run deployment commands there (Docker pre-installed)

**Option C: Install Docker Desktop**
- Windows: https://docs.docker.com/desktop/install/windows-install/
- Mac: https://docs.docker.com/desktop/install/mac-install/
- Linux: https://docs.docker.com/engine/install/

### Issue: Container App not starting

**Check logs**:
```bash
az containerapp revision list \
  --name <AZURE_CONTAINER_APP_NAME> \
  --resource-group <RESOURCE_GROUP_NAME>
```

**Common causes**:
- Missing environment variables (Azure OpenAI endpoint/key)
- Container image pull failures (check registry authentication)
- Port mismatch (backend should run on port 8000)

### Issue: WebSocket connection fails from frontend

**Verify**:
1. API key is correct (check `azd env get-values`)
2. CORS is enabled in APIM (should be enabled by default)
3. Subscription key is passed in query parameter (browsers can't set WebSocket headers)

**Test connection**:
```bash
# Check APIM endpoint
curl https://<APIM_GATEWAY_URL>/inference/openai/realtime?api-key=<KEY>
# Should return 400 (WebSocket upgrade required) not 401 (unauthorized)
```

### Issue: No audio response

**Possible causes**:
1. Browser audio context not initialized (requires user interaction)
2. Microphone permissions not granted
3. Backend VAD threshold too high (speech not detected)

**Check backend logs** for:
- `🔊 Audio delta received` - Confirms audio is being generated
- `📢 Response started` - Confirms AI is responding
- Audio delta size should be >0 bytes

### Issue: Slow interruption response

**Solution**: Lower VAD threshold in `backend/main.py`:
```python
"threshold": 0.4  # Lower value = faster detection
"silence_duration_ms": 400  # Shorter silence = quicker response
```

## Manual Deployment (Without azd)

If `azd` fails or you don't have Docker Desktop installed, you can deploy manually using **ACR Cloud Build** (no local Docker needed):

### 1. Deploy Infrastructure
```bash
# Login to Azure
az login

# Create resource group
az group create --name <your-rg> --location swedencentral

# Deploy Bicep template
az deployment group create \
  --resource-group <your-rg> \
  --template-file main.bicep \
  --parameters @main.parameters.json \
  --parameters environmentName=<your-env-name>
```

### 2. Build Docker Image in Azure (No local Docker needed!)

```bash
# Get registry name from deployment outputs
ACR_NAME=$(az deployment group show -g <your-rg> -n main --query properties.outputs.AZURE_CONTAINER_REGISTRY_NAME.value -o tsv)

# Build image directly in ACR (cloud build)
az acr build --registry $ACR_NAME \
  --image nbk-backend:latest \
  --platform linux/amd64 \
  --file Dockerfile \
  .
```

**Why this works without local Docker:**
- ACR (Azure Container Registry) has built-in cloud build capability
- The image is built in Azure, not on your laptop
- Perfect for machines without Docker Desktop installed

### 3. Update Container App
```bash
CONTAINER_APP_NAME=$(az deployment group show -g <your-rg> -n main --query properties.outputs.AZURE_CONTAINER_APP_NAME.value -o tsv)

az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group <your-rg> \
  --image ${ACR_NAME}.azurecr.io/nbk-backend:latest
```

### Alternative: Use Docker Locally (if Docker Desktop is installed)
```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build and push from your laptop
docker buildx build --platform linux/amd64 \
  -t ${ACR_NAME}.azurecr.io/nbk-backend:latest \
  --push .
```

## Cleanup

To remove all deployed resources:

```bash
azd down --purge
```

This will:
- Delete all Azure resources
- Remove the resource group
- Clean up local environment configuration

**⚠️ Warning**: This action is irreversible. All data and configurations will be lost.

## Security Considerations

### Protecting the API Key

The APIM subscription key should be:
- **Never committed to source control**
- Stored in Azure Key Vault for production
- Rotated regularly (via APIM portal)
- Used with IP restrictions in production

### Enabling Managed Identity (Recommended for Production)

Instead of using API keys between APIM and Azure OpenAI:

1. Enable Managed Identity on APIM
2. Grant APIM identity "Cognitive Services OpenAI User" role on Azure OpenAI
3. Update APIM policy to use managed identity authentication

### Network Isolation

For production deployments:
- Deploy Container Apps in a VNet
- Use Private Endpoints for Azure OpenAI
- Enable VNet integration for Container Apps Environment
- Configure NSG rules to restrict traffic

## Frontend Integration

### JavaScript/TypeScript Example

```typescript
const WEBSOCKET_URL = "wss://your-apim.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime&api-key=YOUR-KEY";

const ws = new WebSocket(WEBSOCKET_URL);

ws.onopen = () => {
  console.log("Connected to NBK Assistant");
  
  // Start streaming audio
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      // Process audio and send via WebSocket
      // See test-frontend-vad.html for full implementation
    });
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'response.audio.delta') {
    // Play audio chunk
    playAudioChunk(message.delta);
  }
};
```

### React/Next.js Integration

See `test-frontend-vad.html` for a complete browser implementation that can be adapted to React hooks.

## Cost Estimation

Approximate monthly costs (Sweden Central region):

| Resource | Tier | Est. Cost/Month |
|----------|------|-----------------|
| Azure OpenAI (Realtime) | Pay-per-token | $0.06/1K audio input tokens, $0.24/1K audio output tokens |
| API Management | Basic | ~$50 |
| Container App | 0.5 vCPU, 1GB RAM | ~$30 |
| Container Registry | Basic | ~$5 |
| App Insights + Log Analytics | Pay-per-GB | ~$10-50 (depends on usage) |
| **Total** | | **~$95-135/month** (excluding Azure OpenAI usage) |

Azure OpenAI costs depend on usage:
- 1 hour of continuous conversation ≈ $2-5
- Average customer call (5 minutes) ≈ $0.15-0.30

## Support and Resources

- **Azure OpenAI Realtime API Documentation**: https://learn.microsoft.com/azure/ai-services/openai/realtime-audio-quickstart
- **Azure Container Apps Documentation**: https://learn.microsoft.com/azure/container-apps/
- **Azure API Management Documentation**: https://learn.microsoft.com/azure/api-management/
- **Azure Developer CLI**: https://learn.microsoft.com/azure/developer/azure-developer-cli/

## Next Steps

1. **Expand NBK Knowledge Base**: Add more pages from nbk.com
2. **Implement Function Calling**: Allow the assistant to look up account information, make transactions, etc.
3. **Add Multi-language Support**: Configure instructions for Arabic/English switching
4. **Integrate with CRM**: Connect to customer database for personalized responses
5. **Implement Call Recording**: Store conversations for quality assurance
6. **Add Authentication**: Implement user authentication before allowing access
7. **Set up CI/CD**: Automate deployments with GitHub Actions or Azure DevOps

---

**Version**: 1.0  
**Last Updated**: November 15, 2025  
**Maintained By**: NBK Digital Team
