# NBK Realtime Speech-to-Speech Assistant

Real-time speech-to-speech AI assistant for National Bank of Kuwait, powered by Azure OpenAI Realtime API with web-scraped knowledge grounding.

## 🌟 Features

- **Real-time Speech-to-Speech**: Bidirectional audio streaming with low latency
- **Arabic Language Support**: Automatic detection and response in Arabic or English
- **NBK Knowledge Base**: Grounded on National Bank of Kuwait website information (web-scraped)
- **Voice Activity Detection**: Server-side VAD automatically detects user speech
- **Echo Voice**: Professional, deeper tone suitable for banking applications
- **Interruption Handling**: Configurable interruption support (experimental)
- **APIM Gateway**: Secure two-layer authentication (subscription key + managed identity)
- **Zero-Config Deployment**: Full automation with `azd up` - no manual configuration needed

## 🏗️ Architecture

```
┌─────────────────┐
│  Frontend App   │  (Web, Mobile, On-Prem)
│  JavaScript/    │
│  Python/C#      │
└────────┬────────┘
         │ WebSocket + api-key header
         │
         ▼
┌─────────────────────────────────────────────────────┐
│          Azure API Management (APIM)                │
│  ┌───────────────────────────────────────────────┐  │
│  │ Subscription Key Authentication               │  │
│  │ (Frontend → APIM)                             │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │ Managed Identity Authentication               │  │
│  │ (APIM → Azure OpenAI)                         │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────┘
                  │ Automatic token generation
                  │
                  ▼
          ┌───────────────────┐
          │  Azure OpenAI     │
          │  gpt-realtime     │
          │  (Sweden Central) │
          └───────────────────┘
```

### Authentication Layers

1. **Frontend → APIM**: Subscription key authentication via `api-key` header
   - Public endpoint accessible from anywhere (web, mobile, on-prem)
   - Single API key shared with frontend teams

2. **APIM → Azure OpenAI**: System-Assigned Managed Identity
   - Automatic Azure AD token generation
   - No credentials stored in code or configuration
   - Policy: `authentication-managed-identity` with `https://cognitiveservices.azure.com` resource

### Knowledge Grounding

The assistant uses **web scraping** instead of Bing Search API (retiring August 2025) or Azure AI Search:

1. **Scraper**: `scrape_nbk.py` uses BeautifulSoup to extract content from nbk.com
2. **Storage**: Scraped content saved to `nbk_knowledge.json` (committed to repo)
3. **Integration**: Knowledge loaded into system prompt at session start
4. **Automation**: Post-deployment hook automatically runs scraper on fresh deployments

**Why web scraping?**
- Bing Search API retiring in August 2025
- Azure AI Search requires complex setup (indexes, chunking, embeddings)
- NBK website has public information suitable for scraping
- Simple, maintainable, zero-config solution

## 📋 Prerequisites

- **Azure Subscription**: Active subscription with Contributor access
- **Azure Developer CLI (azd)**: [Install here](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- **Python 3.11+**: For local testing (not required for frontend integration)
- **PyAudio**: For microphone/speaker access (local testing only)
- **Git**: For cloning the repository

## 🚀 Deployment

### One-Command Deployment

This project is designed for **zero-configuration deployment** on customer tenants:

```powershell
# 1. Clone repository
git clone <repo-url>
cd "S2S Realtime NBK"

# 2. Login to Azure
azd auth login

# 3. Deploy everything (infrastructure + scraper + configuration)
azd up
```

### What Happens During Deployment

1. **Infrastructure Deployment** (via Bicep):
   - Azure API Management (APIM) with subscription key
   - Azure OpenAI with gpt-realtime model (Sweden Central)
   - Application Insights for monitoring
   - Log Analytics workspace
   - System-Assigned Managed Identity for APIM
   - Role assignment: APIM → Azure OpenAI (Cognitive Services User)

2. **Post-Deployment Automation** (via `infra/hooks/postprovision.ps1`):
   - Creates Python virtual environment
   - Installs requirements from `requirements.txt`
   - Runs `scrape_nbk.py` to fetch NBK knowledge base
   - Extracts azd outputs (WebSocket URL, API key, etc.)
   - Displays formatted connection information
   - Saves `deployment-config.txt` for frontend team

3. **Output** (displayed in terminal):
   ```
   ========================================
   NBK Realtime API - Deployment Complete
   ========================================

   WebSocket URL:
     wss://apim-xxxxx.azure-api.net/inference/openai/realtime?api-version=2024-10-01-preview

   API Key (Subscription):
     xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

   Authentication Header:
     api-key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

   Deployment Details:
     Resource Group: rg-xxxxx
     Region: uksouth
     API Version: 2024-10-01-preview
   ```

### Frontend Integration

After deployment, share the following with your frontend team:

1. **Connection Details**: See `deployment-config.txt` or run `.\scripts\get-connection-info.ps1`
2. **Integration Guide**: See `FRONTEND.md` for code examples in JavaScript, Python, and C#
3. **Test Client**: Run `python examples\test-client.py` to validate the backend

**No additional configuration needed!** Frontend teams can start integrating immediately.

## 🧪 Testing

### Validate Deployment

```powershell
# Run validation script
.\scripts\test-deployment.ps1

# Or with verbose output
.\scripts\test-deployment.ps1 -Verbose
```

### Test WebSocket Connection

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run test client
python examples\test-client.py
```

### Run Full Application (Local)

```powershell
# Install PyAudio for microphone/speaker access
pip install pyaudio

# Run main application
python main.py
```

## 📁 Project Structure

```
S2S Realtime NBK/
├── examples/
│   └── test-client.py          # WebSocket connection test
├── infra/
│   └── hooks/
│       └── postprovision.ps1   # Post-deployment automation
├── modules/                     # Bicep infrastructure modules
│   ├── apim.bicep              # API Management configuration
│   ├── foundry.bicep           # Azure OpenAI deployment
│   └── ...
├── scripts/
│   ├── get-connection-info.ps1 # Display connection details
│   └── test-deployment.ps1     # Validate deployment
├── main.py                      # Local speech-to-speech client
├── scrape_nbk.py               # Web scraper for NBK knowledge
├── config.py                   # Configuration and instructions
├── nbk_knowledge.json          # Scraped NBK website content
├── main.bicep                  # Main infrastructure template
├── main.parameters.json        # Deployment parameters
├── FRONTEND.md                 # Frontend integration guide
└── README.md                   # This file
```

## 📁 Project Structure

```
S2S Realtime NBK/
├── modules/                    # Bicep infrastructure modules
│   ├── apim.bicep             # API Management configuration
│   ├── appinsights.bicep      # Application Insights configuration
│   ├── foundry.bicep          # AI Foundry configuration
│   └── workspaces.bicep       # Log Analytics workspace
├── main.bicep                  # Main Bicep deployment template
├── main.py                     # Main application entry point
├── config.py                   # Configuration management
├── utils.py                    # Utility functions
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .env                       # Your environment variables (not in git)
├── params.json                # Generated deployment parameters
└── README.md                  # This file
```

## 🔧 Configuration

### Azure Configuration

The application automatically creates the following Azure resources:

- **Resource Group**: Container for all resources
- **Log Analytics Workspace**: Centralized logging
- **Application Insights**: Application monitoring
- **API Management (APIM)**: API gateway and security
- **AI Foundry**: AI services hub
- **AI Services**: OpenAI Realtime model deployment
- **Container Registry**: For container-based services (if needed)
- **Container Apps**: For MCP servers (if needed)

### Bing Grounding Configuration

Configure how the application searches and grounds information:

```ini
# Target domain for grounding
NBK_DOMAIN=nbk.com
NBK_SITE_FILTER=site:nbk.com

## 🔧 Configuration

### Environment Variables

The application uses these environment variables (auto-configured by `azd up`):

```ini
# APIM Connection (auto-populated by deployment)
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
