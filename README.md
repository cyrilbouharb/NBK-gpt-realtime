# NBK Realtime Speech-to-Speech Assistant# NBK Realtime Voice Assistant# NBK Realtime Speech-to-Speech Assistant



Real-time speech-to-speech AI assistant for National Bank of Kuwait, powered by Azure OpenAI Realtime API with web-scraped knowledge grounding.



## 🌟 FeaturesA production-ready speech-to-speech voice assistant for National Bank of Kuwait (NBK) powered by Azure OpenAI Realtime API with automatic knowledge injection.Real-time speech-to-speech AI assistant for National Bank of Kuwait, powered by Azure OpenAI Realtime API with web-scraped knowledge grounding.



- **Real-time Speech-to-Speech**: Bidirectional audio streaming with low latency

- **Arabic Language Support**: Automatic detection and response in Arabic or English

- **NBK Knowledge Base**: Grounded on National Bank of Kuwait website information (web-scraped)## Overview## 🌟 Features

- **Voice Activity Detection**: Server-side VAD automatically detects user speech

- **Echo Voice**: Professional, deeper tone suitable for banking applications

- **Interruption Handling**: Configurable interruption support

- **APIM Gateway**: Secure two-layer authentication (subscription key + managed identity)This solution provides a fully-managed voice assistant that:- **Real-time Speech-to-Speech**: Bidirectional audio streaming with low latency

- **Zero-Config Deployment**: Full automation with `azd up` - no manual configuration needed

- **Remote Docker Build**: Builds in Azure - no local Docker installation required- ✅ Responds in natural speech using Azure OpenAI GPT-4o Realtime model- **Arabic Language Support**: Automatic detection and response in Arabic or English



## 🏗️ Architecture- ✅ Automatically injects NBK knowledge base into every conversation- **NBK Knowledge Base**: Grounded on National Bank of Kuwait website information (web-scraped)



```- ✅ Supports voice interruption (barge-in) during AI responses- **Voice Activity Detection**: Server-side VAD automatically detects user speech

┌─────────────────┐

│  Frontend App   │  (Web, Mobile, On-Prem)- ✅ Uses server-side Voice Activity Detection (VAD) for natural conversations- **Echo Voice**: Professional, deeper tone suitable for banking applications

│  JavaScript/    │

│  Python/C#      │- ✅ Secured with Azure API Management subscription key authentication- **Interruption Handling**: Configurable interruption support (experimental)

└────────┬────────┘

         │ WebSocket + api-key header- ✅ Scales automatically based on demand (Azure Container Apps)- **APIM Gateway**: Secure two-layer authentication (subscription key + managed identity)

         │

         ▼- ✅ Provides professional male voice (Echo) optimized for banking- **Zero-Config Deployment**: Full automation with `azd up` - no manual configuration needed

┌─────────────────────────────────────────────────────┐

│          Azure API Management (APIM)                │

│  ┌───────────────────────────────────────────────┐  │

│  │ Subscription Key Authentication               │  │## Architecture## 🏗️ Architecture

│  │ (Frontend → APIM)                             │  │

│  └───────────────────────────────────────────────┘  │

│  ┌───────────────────────────────────────────────┐  │

│  │ Managed Identity Authentication               │  │``````

│  │ (APIM → Azure OpenAI)                         │  │

│  └───────────────────────────────────────────────┘  │Frontend (Browser/Mobile App)┌─────────────────┐

└─────────────────┬───────────────────────────────────┘

                  │    ↓ WebSocket (wss://)│  Frontend App   │  (Web, Mobile, On-Prem)

                  ▼

         ┌─────────────────┐Azure API Management (Subscription Key Auth)│  JavaScript/    │

         │ Container App   │

         │ (FastAPI Proxy) │    ↓│  Python/C#      │

         │ + NBK Knowledge │

         └────────┬────────┘Backend Container App (FastAPI WebSocket Proxy)└────────┬────────┘

                  │

                  ▼    ├─ Loads nbk_knowledge.json (3 KB entries)         │ WebSocket + api-key header

          ┌───────────────────┐

          │  Azure OpenAI     │    ├─ Injects system prompt with NBK info         │

          │  gpt-realtime     │

          │  (Sweden Central) │    ├─ Configures Echo voice & VAD settings         ▼

          └───────────────────┘

```    └─ Proxies to Azure OpenAI Realtime API┌─────────────────────────────────────────────────────┐



### Key Components```│          Azure API Management (APIM)                │



- **Backend**: Python FastAPI WebSocket proxy (`backend/main.py`)│  ┌───────────────────────────────────────────────┐  │

- **Infrastructure**: Bicep templates for Azure resources (`main.bicep`, `modules/`)

- **Knowledge Base**: Scraped NBK website content (`nbk_knowledge.json`)### Key Components│  │ Subscription Key Authentication               │  │

- **Deployment**: Azure Developer CLI with remote Docker builds

│  │ (Frontend → APIM)                             │  │

### Authentication Layers

- **Backend**: Python FastAPI WebSocket proxy (`backend/main.py`)│  └───────────────────────────────────────────────┘  │

1. **Frontend → APIM**: Subscription key authentication via `api-key` header

   - Public endpoint accessible from anywhere (web, mobile, on-prem)- **Infrastructure**: Bicep templates for Azure resources (`main.bicep`, `modules/`)│  ┌───────────────────────────────────────────────┐  │

   - Single API key shared with frontend teams

- **Knowledge Base**: Scraped NBK website content (`nbk_knowledge.json`)│  │ Managed Identity Authentication               │  │

2. **APIM → Azure OpenAI**: System-Assigned Managed Identity

   - Automatic Azure AD token generation- **Frontend Example**: Browser-based test interface (`test-frontend-vad.html`)│  │ (APIM → Azure OpenAI)                         │  │

   - No credentials stored in code or configuration

   - Policy: `authentication-managed-identity` with `https://cognitiveservices.azure.com` resource│  └───────────────────────────────────────────────┘  │



## 📋 Prerequisites## Quick Start└─────────────────┬───────────────────────────────────┘



- **Azure Subscription**: Active subscription with Contributor access                  │ Automatic token generation

- **Azure Developer CLI (azd)**: [Install here](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)

- **Python 3.11+**: For post-provision hook (knowledge scraping)### Prerequisites                  │

- **Git**: For cloning the repository

- **No Docker needed!** Builds remotely in Azure Container Registry                  ▼



## 🚀 One-Command Deployment- Azure subscription          ┌───────────────────┐



This project is designed for **zero-configuration deployment**:- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)          │  Azure OpenAI     │



```powershell- Docker Desktop          │  gpt-realtime     │

# 1. Clone repository

git clone https://github.com/cyrilbouharb/NBK-gpt-realtime.git- PowerShell or Bash          │  (Sweden Central) │

cd NBK-gpt-realtime

          └───────────────────┘

# 2. Login to Azure

azd auth login### Deploy in 3 Steps```



# 3. Deploy everything (10-15 minutes)

azd up

``````bash### Authentication Layers



### What Happens During Deployment# 1. Login to Azure



1. **Infrastructure Deployment** (via Bicep):azd auth login1. **Frontend → APIM**: Subscription key authentication via `api-key` header

   - Azure API Management (APIM) with subscription key

   - Azure OpenAI with gpt-realtime model (Sweden Central)   - Public endpoint accessible from anywhere (web, mobile, on-prem)

   - Azure Container Registry for Docker images

   - Azure Container Apps environment# 2. Initialize environment   - Single API key shared with frontend teams

   - Application Insights for monitoring

   - Log Analytics workspaceazd init

   - System-Assigned Managed Identity for APIM

   - Role assignment: APIM → Azure OpenAI (Cognitive Services User)2. **APIM → Azure OpenAI**: System-Assigned Managed Identity



2. **Docker Build** (remote in Azure):# 3. Deploy everything   - Automatic Azure AD token generation

   - Builds backend Docker image in Azure Container Registry

   - No local Docker installation requiredazd up   - No credentials stored in code or configuration

   - Controlled by `remoteBuild: true` in `azure.yaml`

```   - Policy: `authentication-managed-identity` with `https://cognitiveservices.azure.com` resource

3. **Container Deployment**:

   - Deploys FastAPI backend to Container Apps

   - Configures environment variables (OpenAI endpoint, API key)

   - Sets up auto-scaling (1-3 replicas)**Deployment time**: ~15 minutes### Knowledge Grounding



4. **Post-Deployment Automation** (via `infra/hooks/postprovision.ps1`):

   - Creates Python virtual environment

   - Installs requirements from `requirements.txt`### Get Your EndpointThe assistant uses **web scraping** instead of Bing Search API (retiring August 2025) or Azure AI Search:

   - Runs `scrape_nbk.py` to fetch NBK knowledge base

   - Extracts azd outputs (WebSocket URL, API key, etc.)

   - Displays formatted connection information

   - Saves `deployment-config.txt` for frontend teamAfter deployment:1. **Scraper**: `scrape_nbk.py` uses BeautifulSoup to extract content from nbk.com



5. **Output** (displayed in terminal):2. **Storage**: Scraped content saved to `nbk_knowledge.json` (committed to repo)

   ```

   ================================================================```bash3. **Integration**: Knowledge loaded into system prompt at session start

   FRONTEND CONFIGURATION

   ================================================================azd env get-values4. **Automation**: Post-deployment hook automatically runs scraper on fresh deployments

   

   WebSocket URL:```

     wss://apim-xxxxx.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime

   **Why web scraping?**

   API Key:

     your-subscription-key-hereLook for:- Bing Search API retiring in August 2025

   

   Authentication:- `FULL_WEBSOCKET_URL` - Complete endpoint with API key- Azure AI Search requires complex setup (indexes, chunking, embeddings)

     Add header: api-key: YOUR_KEY

   ```- `APIM_SUBSCRIPTION_KEY` - Your authentication key- NBK website has public information suitable for scraping



## 🔌 Usage- Simple, maintainable, zero-config solution



### Connect from JavaScript (Browser)## Usage



```javascript## 📋 Prerequisites

const ws = new WebSocket("wss://your-apim.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime", [

  "realtime",### Connect from JavaScript

  "your-api-key-here"

]);- **Azure Subscription**: Active subscription with Contributor access



ws.onopen = () => {```javascript- **Azure Developer CLI (azd)**: [Install here](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)

  console.log("Connected to NBK Voice Assistant");

  // Start streaming audio from microphoneconst ws = new WebSocket("wss://your-apim.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime&api-key=YOUR-KEY");- **Python 3.11+**: For local testing (not required for frontend integration)

};

- **PyAudio**: For microphone/speaker access (local testing only)

ws.onmessage = (event) => {

  const msg = JSON.parse(event.data);ws.onopen = () => {- **Git**: For cloning the repository

  if (msg.type === 'response.audio.delta') {

    // Play audio response  console.log("Connected to NBK Voice Assistant");

    playAudio(msg.delta);

  }  // Start streaming audio from microphone## 🚀 Deployment

};

```};



### Connect from Python### One-Command Deployment



```pythonws.onmessage = (event) => {

import websockets

import asyncio  const msg = JSON.parse(event.data);This project is designed for **zero-configuration deployment** on customer tenants:



async def connect_to_nbk():  if (msg.type === 'response.audio.delta') {

    uri = "wss://your-apim.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime"

    headers = {"api-key": "your-subscription-key"}    // Play audio response```powershell

    

    async with websockets.connect(uri, extra_headers=headers) as ws:    playAudio(msg.delta);# 1. Clone repository

        print("Connected!")

        # Send audio, receive responses  }git clone <repo-url>

```

};cd "S2S Realtime NBK"

### Get Your Deployment Info

```

After deployment, retrieve connection details:

# 2. Login to Azure

```powershell

# Get all environment variablesSee `test-frontend-vad.html` for complete browser implementation.azd auth login

azd env get-values



# Get specific values (PowerShell)

azd env get-values | Select-String "FULL_WEBSOCKET_URL"### Test the Deployment# 3. Deploy everything (infrastructure + scraper + configuration)

azd env get-values | Select-String "APIM_SUBSCRIPTION_KEY"

azd up

# Linux/Mac

azd env get-values | grep FULL_WEBSOCKET_URL```bash```

```

# Check backend health

Configuration is also saved to `deployment-config.txt`.

curl https://ca-nbk-backend-<suffix>.azurecontainerapps.io/health### What Happens During Deployment

## 🔧 Configuration



### Update NBK Knowledge

# View backend logs1. **Infrastructure Deployment** (via Bicep):

```powershell

# 1. Edit scrape_nbk.py to add/modify URLsaz containerapp logs show --name <CONTAINER_APP_NAME> --resource-group <RG_NAME> --follow   - Azure API Management (APIM) with subscription key

# 2. Run scraper

python scrape_nbk.py```   - Azure OpenAI with gpt-realtime model (Sweden Central)



# 3. Redeploy backend   - Application Insights for monitoring

azd deploy

```## Configuration   - Log Analytics workspace



### Adjust Voice Settings   - System-Assigned Managed Identity for APIM



Edit `backend/main.py`:### Update NBK Knowledge   - Role assignment: APIM → Azure OpenAI (Cognitive Services User)



```python

# Change voice (line ~131)

"voice": "echo"  # Options: alloy, ash, ballad, coral, echo, sage, shimmer, verse1. Edit `scrape_nbk.py` to add/modify URLs2. **Post-Deployment Automation** (via `infra/hooks/postprovision.ps1`):



# Adjust VAD sensitivity (lines ~134-138)2. Run: `python scrape_nbk.py`   - Creates Python virtual environment

"turn_detection": {

    "threshold": 0.5,           # Lower = more sensitive (0.0-1.0)3. Deploy: `azd deploy backend`   - Installs requirements from `requirements.txt`

    "silence_duration_ms": 500  # Lower = faster response

}   - Runs `scrape_nbk.py` to fetch NBK knowledge base



# Enable/disable interruptions (line ~140)### Adjust Voice Settings   - Extracts azd outputs (WebSocket URL, API key, etc.)

"input_audio_transcription": {

    "model": "whisper-1"   - Displays formatted connection information

}

```Edit `backend/main.py`:   - Saves `deployment-config.txt` for frontend team



After changes:

```powershell

azd deploy```python3. **Output** (displayed in terminal):

```

# Change voice (line 131)   ```

## 📊 Monitoring & Logs

"voice": "echo"  # Options: alloy, ash, ballad, coral, echo, sage, shimmer, verse   ========================================

```powershell

# View all logs in Application Insights   NBK Realtime API - Deployment Complete

azd monitor

# Adjust VAD sensitivity (lines 134-138)   ========================================

# View Container App logs

az containerapp logs show \"turn_detection": {

  --name <CONTAINER_APP_NAME> \

  --resource-group <RESOURCE_GROUP> \    "threshold": 0.5,           # Lower = more sensitive   WebSocket URL:

  --follow

    "silence_duration_ms": 500  # Lower = faster response     wss://apim-xxxxx.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview

# Check backend health

curl https://<CONTAINER_APP_FQDN>/health}

```

```   API Key (Subscription):

## 🧪 Testing

     xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Test your deployment:

Then redeploy: `azd deploy backend`

```powershell

# Run included test script   Authentication Header:

.\scripts\test-deployment.ps1

## Project Structure     api-key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Or test manually with WebSocket client

# See nbk-frontend.html for browser-based test

```

```   Deployment Details:

## 🔄 Update Workflow

.     Resource Group: rg-xxxxx

```powershell

# Update code only (fast)├── backend/                    # FastAPI WebSocket proxy     Region: uksouth

azd deploy

│   ├── main.py                # Main application logic     API Version: 2024-10-01-preview

# Update infrastructure + code

azd up│   └── requirements.txt       # Python dependencies   ```



# View current configuration├── modules/                    # Bicep infrastructure modules

azd env get-values

│   ├── apim.bicep             # API Management### Frontend Integration

# Clean up resources

azd down│   ├── containerapp.bicep     # Container App + Environment

```

│   ├── foundry.bicep          # Azure OpenAIAfter deployment, share the following with your frontend team:

## 📁 Project Structure

│   └── registry.bicep         # Container Registry

```

.├── infra/hooks/               # Post-deployment scripts1. **Connection Details**: See `deployment-config.txt` or run `.\scripts\get-connection-info.ps1`

├── azure.yaml                  # azd configuration (remoteBuild enabled)

├── main.bicep                  # Main infrastructure template│   └── postprovision.ps1      # Scrapes NBK knowledge2. **Integration Guide**: See `FRONTEND.md` for code examples in JavaScript, Python, and C#

├── main.parameters.json        # Deployment parameters

├── Dockerfile                  # Container image definition├── main.bicep                 # Main infrastructure template3. **Test Client**: Run `python examples\test-client.py` to validate the backend

├── nbk_knowledge.json          # Scraped NBK knowledge (auto-generated)

├── scrape_nbk.py              # Knowledge base scraper├── main.parameters.json       # Infrastructure parameters

├── requirements.txt           # Python dependencies

├── backend/├── azure.yaml                 # Azure Developer CLI config**No additional configuration needed!** Frontend teams can start integrating immediately.

│   ├── main.py               # FastAPI WebSocket proxy

│   └── requirements.txt      # Backend dependencies├── Dockerfile                 # Backend container image

├── infra/

│   └── hooks/├── nbk_knowledge.json         # NBK knowledge base## 🧪 Testing

│       └── postprovision.ps1 # Post-deployment automation

├── modules/                   # Bicep modules├── scrape_nbk.py              # Knowledge scraper

│   ├── apim.bicep

│   ├── foundry.bicep└── DEPLOYMENT_GUIDE.md        # Comprehensive deployment docs### Validate Deployment

│   ├── registry.bicep

│   ├── containerapp.bicep```

│   └── ...

└── scripts/```powershell

    └── test-deployment.ps1   # Deployment test script

```## Features# Run validation script



## 🎯 Why Web Scraping?.\scripts\test-deployment.ps1



The assistant uses **web scraping** instead of:### ✅ Automatic Knowledge Injection



- **Bing Search API** (retiring August 2025)# Or with verbose output

- **Azure AI Search** (requires complex setup: indexes, chunking, embeddings)

The backend automatically:.\scripts\test-deployment.ps1 -Verbose

**Benefits:**

- Simple, maintainable, zero-config solution1. Loads `nbk_knowledge.json` on startup```

- NBK website has public information suitable for scraping

- Automatically updates knowledge base on each deployment2. Builds a system prompt with NBK information

- No additional Azure services required

3. Injects it into every WebSocket session### Test WebSocket Connection

## 🤝 Contributing

4. No manual configuration needed

1. Make changes to code or infrastructure

2. Test locally if possible```powershell

3. Deploy with `azd up` or `azd deploy`

4. Commit changes### ✅ Voice Interruption Support# Activate virtual environment

5. Push to repository

.\venv\Scripts\Activate.ps1

## 📄 License

Users can interrupt the AI mid-sentence:

[Your License Here]

- Backend detects new speech via Azure OpenAI VAD# Run test client

## 🆘 Support

- Automatically cancels current responsepython examples\test-client.py

For issues or questions:

1. Check `deployment-config.txt` for your current configuration- Processes the new user input immediately```

2. View logs with `azd monitor`

3. Review Application Insights in Azure Portal

4. Check Container App logs for backend issues

### ✅ Production-Ready Security### Run Full Application (Local)

## 🔗 Related Documentation



- [QUICK_START.md](./QUICK_START.md) - Quick reference guide

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Detailed deployment instructions- API key authentication via APIM```powershell

- [Azure OpenAI Realtime API](https://learn.microsoft.com/azure/ai-services/openai/realtime-audio-quickstart)

- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/overview)- No Azure OpenAI credentials exposed to frontend# Install PyAudio for microphone/speaker access


- Container Registry with admin authenticationpip install pyaudio

- Secrets managed as Container App secrets

# Run main application

### ✅ Enterprise Monitoringpython main.py

```

- Application Insights for application telemetry

- Log Analytics for centralized logging## 📁 Project Structure

- Container App log streaming

- APIM analytics for API usage tracking```

S2S Realtime NBK/

## Monitoring├── examples/

│   └── test-client.py          # WebSocket connection test

### View Logs├── infra/

│   └── hooks/

```bash│       └── postprovision.ps1   # Post-deployment automation

# Container App logs (real-time)├── modules/                     # Bicep infrastructure modules

az containerapp logs show --name <APP_NAME> --resource-group <RG> --follow│   ├── apim.bicep              # API Management configuration

│   ├── foundry.bicep           # Azure OpenAI deployment

# Application Insights (Azure Portal)│   └── ...

# Navigate to: Resource Group → Application Insights → Logs├── scripts/

```│   ├── get-connection-info.ps1 # Display connection details

│   └── test-deployment.ps1     # Validate deployment

### Health Check├── main.py                      # Local speech-to-speech client

├── scrape_nbk.py               # Web scraper for NBK knowledge

```bash├── config.py                   # Configuration and instructions

curl https://<BACKEND_FQDN>/health├── nbk_knowledge.json          # Scraped NBK website content

```├── main.bicep                  # Main infrastructure template

├── main.parameters.json        # Deployment parameters

Expected response:├── FRONTEND.md                 # Frontend integration guide

```json└── README.md                   # This file

{```

  "status": "healthy",

  "knowledge_entries": 3,## 📁 Project Structure

  "instructions_length": 2211

}```

```S2S Realtime NBK/

├── modules/                    # Bicep infrastructure modules

## Troubleshooting│   ├── apim.bicep             # API Management configuration

│   ├── appinsights.bicep      # Application Insights configuration

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed troubleshooting steps.│   ├── foundry.bicep          # AI Foundry configuration

│   └── workspaces.bicep       # Log Analytics workspace

Common issues:├── main.bicep                  # Main Bicep deployment template

- **WebSocket connection fails**: Check API key and query parameter format├── main.py                     # Main application entry point

- **No audio response**: Verify browser microphone permissions and audio context├── config.py                   # Configuration management

- **Slow interruption**: Lower VAD threshold in backend configuration├── utils.py                    # Utility functions

├── requirements.txt            # Python dependencies

## Cost Estimation├── .env.example               # Environment variables template

├── .env                       # Your environment variables (not in git)

~$95-135/month (excluding Azure OpenAI usage):├── params.json                # Generated deployment parameters

- Azure OpenAI: Pay-per-token (~$0.15-0.30 per 5-minute call)└── README.md                  # This file

- APIM Basic: ~$50/month```

- Container App: ~$30/month

- Container Registry: ~$5/month## 🔧 Configuration

- Monitoring: ~$10-50/month

### Azure Configuration

## Next Steps

The application automatically creates the following Azure resources:

1. **Expand Knowledge**: Add more NBK pages to `scrape_nbk.py`

2. **Add Functions**: Implement account lookups, transactions, etc.- **Resource Group**: Container for all resources

3. **Multi-language**: Add Arabic language support- **Log Analytics Workspace**: Centralized logging

4. **Authentication**: Integrate customer authentication- **Application Insights**: Application monitoring

5. **CI/CD**: Set up GitHub Actions for automated deployments- **API Management (APIM)**: API gateway and security

- **AI Foundry**: AI services hub

## Documentation- **AI Services**: OpenAI Realtime model deployment

- **Container Registry**: For container-based services (if needed)

- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Complete deployment instructions- **Container Apps**: For MCP servers (if needed)

- [Azure OpenAI Realtime API Docs](https://learn.microsoft.com/azure/ai-services/openai/realtime-audio-quickstart)

- [Azure Container Apps Docs](https://learn.microsoft.com/azure/container-apps/)### Bing Grounding Configuration



## SupportConfigure how the application searches and grounds information:



For issues or questions:```ini

1. Check [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) troubleshooting section# Target domain for grounding

2. Review Azure Container App logsNBK_DOMAIN=nbk.com

3. Check Application Insights for errorsNBK_SITE_FILTER=site:nbk.com



## License## 🔧 Configuration



This project is for internal use by National Bank of Kuwait.### Environment Variables



---The application uses these environment variables (auto-configured by `azd up`):



**Status**: Production Ready  ```ini

**Last Updated**: November 15, 2025# APIM Connection (auto-populated by deployment)

APIM_GATEWAY_URL=https://apim-xxxxx.azure-api.net
APIM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
INFERENCE_API_PATH=inference
INFERENCE_API_VERSION=2024-10-01-preview

# Not used (Bing Search API retiring August 2025)
# BING_API_KEY=
```

### Session Configuration

Customize voice and behavior in `main.py` or `config.py`:

```python
session_config = {
    "modalities": ["audio", "text"],  # Required: both modalities
    "voice": "echo",                   # Professional banking voice
    "input_audio_format": "pcm16",
    "output_audio_format": "pcm16",
    "turn_detection": {
        "type": "server_vad",
        "threshold": 0.2,              # Lower = more sensitive
        "silence_duration_ms": 600,
        "prefix_padding_ms": 100
    }
}
```

### Knowledge Base

The `nbk_knowledge.json` file contains scraped content from:
- nbk.com/personal (Personal Banking)
- nbk.com/business (Business Banking)
- nbk.com/contact (Contact Information)

To update the knowledge base:

```powershell
python scrape_nbk.py
```

## 💡 Usage

### Run Locally with Microphone/Speaker

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run main application
python main.py
```

The application will:
1. List available audio devices
2. Prompt you to select microphone and speaker
3. Connect to the Realtime API
4. Enable voice conversation with NBK assistant

### Test Connection Without Audio

```powershell
python examples\test-client.py
```

This validates:
- WebSocket connectivity
- Authentication
- Session configuration
- Text and audio streaming

### Display Connection Info

```powershell
# Display in terminal
.\scripts\get-connection-info.ps1

# Copy to clipboard
.\scripts\get-connection-info.ps1 -CopyToClipboard

# Save to file
.\scripts\get-connection-info.ps1 -SaveToFile
```

## 🔐 Security

### Authentication

**Two-layer authentication model:**

1. **Frontend → APIM** (Public)
   - Subscription key via `api-key` header
   - Accessible from anywhere (web, mobile, on-prem)
   - Single key shared with frontend teams

2. **APIM → Azure OpenAI** (Backend)
   - System-Assigned Managed Identity
   - Automatic Azure AD token generation
   - No credentials stored or managed manually

### Best Practices

- **Never commit `.env`** with API keys to version control (already in `.gitignore`)
- **Rotate subscription keys** periodically via APIM portal
- **Monitor usage** via Application Insights
- **Use Azure Key Vault** for production secrets (optional enhancement)

### APIM Policy

The deployed policy (`policy.xml`):

```xml
<policies>
  <inbound>
    <base />
    <authentication-managed-identity resource="https://cognitiveservices.azure.com" />
  </inbound>
</policies>
```

This automatically authenticates APIM to Azure OpenAI using its managed identity.

## 📊 Monitoring

### Application Insights

View real-time metrics:

```powershell
# Get Application Insights name
azd env get-values | Select-String "APPLICATION_INSIGHTS"

# Open in portal
az monitor app-insights component show \
  --resource-group <resource-group-name> \
  --app <app-insights-name>
```

### Log Analytics

Query logs using KQL in Azure Portal:

```kql
// Recent API requests
ApiManagementGatewayLogs
| where TimeGenerated > ago(1h)
| project TimeGenerated, ApiId, Method, Url, ResponseCode

// Model usage
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.COGNITIVESERVICES"
| where TimeGenerated > ago(1h)
```

## 🛠️ Troubleshooting

### Deployment Issues

**Problem**: `azd up` fails with resource already exists
```powershell
# Solution: Delete existing deployment and retry
azd down
azd up
```

**Problem**: Bicep deployment timeout
```powershell
# Solution: Check Azure Portal for deployment status
az deployment group show \
  --resource-group <rg-name> \
  --name <deployment-name>
```

### Connection Issues

**Problem**: WebSocket connection fails with 401
```
# Solution: Verify API key is correct
azd env get-values | Select-String "APIM_SUBSCRIPTION_KEY"
```

**Problem**: WebSocket connection fails with timeout
```
# Solution: Check APIM endpoint is accessible
Test-NetConnection -ComputerName apim-xxxxx.azure-api.net -Port 443
```

### Audio Issues

**Problem**: No audio devices listed
```
# Solution: Install PyAudio
pip install pyaudio

# On Windows, you may need to install from wheel:
pip install pipwin
pipwin install pyaudio
```

**Problem**: Audio choppy or delayed
```
# Solution: Adjust chunk size in main.py
CHUNK_SIZE = 480  # 20ms at 24kHz (default)
CHUNK_SIZE = 240  # 10ms - try smaller chunks
```

### Knowledge Base Issues

**Problem**: NBK knowledge not up to date
```powershell
# Solution: Re-run scraper
python scrape_nbk.py
```

**Problem**: Scraper fails to fetch pages
```
# Solution: Check network connectivity and NBK website status
# The scraper handles failures gracefully but logs errors
```

## 📚 Additional Resources

- [Azure OpenAI Realtime API Documentation](https://learn.microsoft.com/azure/ai-services/openai/realtime-audio)
- [APIM Managed Identity Authentication](https://learn.microsoft.com/azure/api-management/api-management-authentication-policies)
- [Frontend Integration Guide](./FRONTEND.md)
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/)

## 🤝 Support

For questions or issues:

1. Run validation: `.\scripts\test-deployment.ps1`
2. Review logs in Application Insights
3. Check frontend integration guide: `FRONTEND.md`
4. Contact deployment team

## 📄 License

Internal use only - National Bank of Kuwait

---

**Quick Reference:**

```powershell
# Deploy everything
azd up

# Get connection info
.\scripts\get-connection-info.ps1

# Validate deployment
.\scripts\test-deployment.ps1

# Test connection
python examples\test-client.py

# Run locally with audio
python main.py

# Update knowledge base
python scrape_nbk.py

# Clean up
azd down
```

### Adding Audio Mode

The application currently runs in text mode. To add audio support, modify `main.py` to handle audio input/output using the existing Realtime API infrastructure.

## 📚 References

- [Azure OpenAI Realtime API](https://learn.microsoft.com/azure/ai-services/openai/realtime-audio-quickstart)
- [Bing Web Search API](https://learn.microsoft.com/bing/search-apis/bing-web-search/overview)
- [Azure API Management](https://learn.microsoft.com/azure/api-management/)
- [Semantic Kernel](https://learn.microsoft.com/semantic-kernel/overview/)
- [Azure Bicep](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)

## 📄 License

This project is provided as-is for demonstration purposes.

## 🤝 Contributing

This is a proof-of-concept application. For production use, consider:

- Adding comprehensive error handling
- Implementing retry logic
- Adding authentication/authorization
- Setting up CI/CD pipelines
- Adding unit and integration tests
- Implementing proper logging

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review Azure and Bing API documentation
3. Check Application Insights for runtime errors

---

**Note**: This application demonstrates integration between Azure OpenAI Realtime API and Bing custom grounding. Ensure you have appropriate licenses and permissions for all services used.
