# NBK Realtime Voice Assistant# NBK Realtime Speech-to-Speech Assistant



A production-ready speech-to-speech voice assistant for National Bank of Kuwait (NBK) powered by Azure OpenAI Realtime API with automatic knowledge injection.Real-time speech-to-speech AI assistant for National Bank of Kuwait, powered by Azure OpenAI Realtime API with web-scraped knowledge grounding.



## Overview## 🌟 Features



This solution provides a fully-managed voice assistant that:- **Real-time Speech-to-Speech**: Bidirectional audio streaming with low latency

- ✅ Responds in natural speech using Azure OpenAI GPT-4o Realtime model- **Arabic Language Support**: Automatic detection and response in Arabic or English

- ✅ Automatically injects NBK knowledge base into every conversation- **NBK Knowledge Base**: Grounded on National Bank of Kuwait website information (web-scraped)

- ✅ Supports voice interruption (barge-in) during AI responses- **Voice Activity Detection**: Server-side VAD automatically detects user speech

- ✅ Uses server-side Voice Activity Detection (VAD) for natural conversations- **Echo Voice**: Professional, deeper tone suitable for banking applications

- ✅ Secured with Azure API Management subscription key authentication- **Interruption Handling**: Configurable interruption support (experimental)

- ✅ Scales automatically based on demand (Azure Container Apps)- **APIM Gateway**: Secure two-layer authentication (subscription key + managed identity)

- ✅ Provides professional male voice (Echo) optimized for banking- **Zero-Config Deployment**: Full automation with `azd up` - no manual configuration needed



## Architecture## 🏗️ Architecture



``````

Frontend (Browser/Mobile App)┌─────────────────┐

    ↓ WebSocket (wss://)│  Frontend App   │  (Web, Mobile, On-Prem)

Azure API Management (Subscription Key Auth)│  JavaScript/    │

    ↓│  Python/C#      │

Backend Container App (FastAPI WebSocket Proxy)└────────┬────────┘

    ├─ Loads nbk_knowledge.json (3 KB entries)         │ WebSocket + api-key header

    ├─ Injects system prompt with NBK info         │

    ├─ Configures Echo voice & VAD settings         ▼

    └─ Proxies to Azure OpenAI Realtime API┌─────────────────────────────────────────────────────┐

```│          Azure API Management (APIM)                │

│  ┌───────────────────────────────────────────────┐  │

### Key Components│  │ Subscription Key Authentication               │  │

│  │ (Frontend → APIM)                             │  │

- **Backend**: Python FastAPI WebSocket proxy (`backend/main.py`)│  └───────────────────────────────────────────────┘  │

- **Infrastructure**: Bicep templates for Azure resources (`main.bicep`, `modules/`)│  ┌───────────────────────────────────────────────┐  │

- **Knowledge Base**: Scraped NBK website content (`nbk_knowledge.json`)│  │ Managed Identity Authentication               │  │

- **Frontend Example**: Browser-based test interface (`test-frontend-vad.html`)│  │ (APIM → Azure OpenAI)                         │  │

│  └───────────────────────────────────────────────┘  │

## Quick Start└─────────────────┬───────────────────────────────────┘

                  │ Automatic token generation

### Prerequisites                  │

                  ▼

- Azure subscription          ┌───────────────────┐

- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)          │  Azure OpenAI     │

- Docker Desktop          │  gpt-realtime     │

- PowerShell or Bash          │  (Sweden Central) │

          └───────────────────┘

### Deploy in 3 Steps```



```bash### Authentication Layers

# 1. Login to Azure

azd auth login1. **Frontend → APIM**: Subscription key authentication via `api-key` header

   - Public endpoint accessible from anywhere (web, mobile, on-prem)

# 2. Initialize environment   - Single API key shared with frontend teams

azd init

2. **APIM → Azure OpenAI**: System-Assigned Managed Identity

# 3. Deploy everything   - Automatic Azure AD token generation

azd up   - No credentials stored in code or configuration

```   - Policy: `authentication-managed-identity` with `https://cognitiveservices.azure.com` resource



**Deployment time**: ~15 minutes### Knowledge Grounding



### Get Your EndpointThe assistant uses **web scraping** instead of Bing Search API (retiring August 2025) or Azure AI Search:



After deployment:1. **Scraper**: `scrape_nbk.py` uses BeautifulSoup to extract content from nbk.com

2. **Storage**: Scraped content saved to `nbk_knowledge.json` (committed to repo)

```bash3. **Integration**: Knowledge loaded into system prompt at session start

azd env get-values4. **Automation**: Post-deployment hook automatically runs scraper on fresh deployments

```

**Why web scraping?**

Look for:- Bing Search API retiring in August 2025

- `FULL_WEBSOCKET_URL` - Complete endpoint with API key- Azure AI Search requires complex setup (indexes, chunking, embeddings)

- `APIM_SUBSCRIPTION_KEY` - Your authentication key- NBK website has public information suitable for scraping

- Simple, maintainable, zero-config solution

## Usage

## 📋 Prerequisites

### Connect from JavaScript

- **Azure Subscription**: Active subscription with Contributor access

```javascript- **Azure Developer CLI (azd)**: [Install here](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)

const ws = new WebSocket("wss://your-apim.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime&api-key=YOUR-KEY");- **Python 3.11+**: For local testing (not required for frontend integration)

- **PyAudio**: For microphone/speaker access (local testing only)

ws.onopen = () => {- **Git**: For cloning the repository

  console.log("Connected to NBK Voice Assistant");

  // Start streaming audio from microphone## 🚀 Deployment

};

### One-Command Deployment

ws.onmessage = (event) => {

  const msg = JSON.parse(event.data);This project is designed for **zero-configuration deployment** on customer tenants:

  if (msg.type === 'response.audio.delta') {

    // Play audio response```powershell

    playAudio(msg.delta);# 1. Clone repository

  }git clone <repo-url>

};cd "S2S Realtime NBK"

```

# 2. Login to Azure

See `test-frontend-vad.html` for complete browser implementation.azd auth login



### Test the Deployment# 3. Deploy everything (infrastructure + scraper + configuration)

azd up

```bash```

# Check backend health

curl https://ca-nbk-backend-<suffix>.azurecontainerapps.io/health### What Happens During Deployment



# View backend logs1. **Infrastructure Deployment** (via Bicep):

az containerapp logs show --name <CONTAINER_APP_NAME> --resource-group <RG_NAME> --follow   - Azure API Management (APIM) with subscription key

```   - Azure OpenAI with gpt-realtime model (Sweden Central)

   - Application Insights for monitoring

## Configuration   - Log Analytics workspace

   - System-Assigned Managed Identity for APIM

### Update NBK Knowledge   - Role assignment: APIM → Azure OpenAI (Cognitive Services User)



1. Edit `scrape_nbk.py` to add/modify URLs2. **Post-Deployment Automation** (via `infra/hooks/postprovision.ps1`):

2. Run: `python scrape_nbk.py`   - Creates Python virtual environment

3. Deploy: `azd deploy backend`   - Installs requirements from `requirements.txt`

   - Runs `scrape_nbk.py` to fetch NBK knowledge base

### Adjust Voice Settings   - Extracts azd outputs (WebSocket URL, API key, etc.)

   - Displays formatted connection information

Edit `backend/main.py`:   - Saves `deployment-config.txt` for frontend team



```python3. **Output** (displayed in terminal):

# Change voice (line 131)   ```

"voice": "echo"  # Options: alloy, ash, ballad, coral, echo, sage, shimmer, verse   ========================================

   NBK Realtime API - Deployment Complete

# Adjust VAD sensitivity (lines 134-138)   ========================================

"turn_detection": {

    "threshold": 0.5,           # Lower = more sensitive   WebSocket URL:

    "silence_duration_ms": 500  # Lower = faster response     wss://apim-xxxxx.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview

}

```   API Key (Subscription):

     xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Then redeploy: `azd deploy backend`

   Authentication Header:

## Project Structure     api-key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx



```   Deployment Details:

.     Resource Group: rg-xxxxx

├── backend/                    # FastAPI WebSocket proxy     Region: uksouth

│   ├── main.py                # Main application logic     API Version: 2024-10-01-preview

│   └── requirements.txt       # Python dependencies   ```

├── modules/                    # Bicep infrastructure modules

│   ├── apim.bicep             # API Management### Frontend Integration

│   ├── containerapp.bicep     # Container App + Environment

│   ├── foundry.bicep          # Azure OpenAIAfter deployment, share the following with your frontend team:

│   └── registry.bicep         # Container Registry

├── infra/hooks/               # Post-deployment scripts1. **Connection Details**: See `deployment-config.txt` or run `.\scripts\get-connection-info.ps1`

│   └── postprovision.ps1      # Scrapes NBK knowledge2. **Integration Guide**: See `FRONTEND.md` for code examples in JavaScript, Python, and C#

├── main.bicep                 # Main infrastructure template3. **Test Client**: Run `python examples\test-client.py` to validate the backend

├── main.parameters.json       # Infrastructure parameters

├── azure.yaml                 # Azure Developer CLI config**No additional configuration needed!** Frontend teams can start integrating immediately.

├── Dockerfile                 # Backend container image

├── nbk_knowledge.json         # NBK knowledge base## 🧪 Testing

├── scrape_nbk.py              # Knowledge scraper

└── DEPLOYMENT_GUIDE.md        # Comprehensive deployment docs### Validate Deployment

```

```powershell

## Features# Run validation script

.\scripts\test-deployment.ps1

### ✅ Automatic Knowledge Injection

# Or with verbose output

The backend automatically:.\scripts\test-deployment.ps1 -Verbose

1. Loads `nbk_knowledge.json` on startup```

2. Builds a system prompt with NBK information

3. Injects it into every WebSocket session### Test WebSocket Connection

4. No manual configuration needed

```powershell

### ✅ Voice Interruption Support# Activate virtual environment

.\venv\Scripts\Activate.ps1

Users can interrupt the AI mid-sentence:

- Backend detects new speech via Azure OpenAI VAD# Run test client

- Automatically cancels current responsepython examples\test-client.py

- Processes the new user input immediately```



### ✅ Production-Ready Security### Run Full Application (Local)



- API key authentication via APIM```powershell

- No Azure OpenAI credentials exposed to frontend# Install PyAudio for microphone/speaker access

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
