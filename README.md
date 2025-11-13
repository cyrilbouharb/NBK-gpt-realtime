# Realtime NBK Application with Bing Custom Grounding

This application implements Azure OpenAI Realtime API with Bing custom grounding for the NBK (National Bank of Kuwait) domain. It provides an intelligent conversational agent that grounds its responses using live information from the NBK website.

## 🌟 Features

- **Azure OpenAI Realtime API**: Real-time conversational AI with text and audio modalities
- **Bing Custom Grounding**: Searches and grounds responses using information from the NBK domain
- **Azure Infrastructure**: Automated deployment using Bicep templates
- **APIM Integration**: API Management for secure and scalable API access
- **AI Foundry**: Integrated AI services and model deployment
- **Caching**: Intelligent caching of grounding results for improved performance
- **Rich CLI**: Beautiful command-line interface with progress indicators

## 📋 Prerequisites

- **Azure Subscription**: Active Azure subscription with appropriate permissions
- **Azure CLI**: Version 2.56.0 or higher ([Install](https://docs.microsoft.com/cli/azure/install-azure-cli))
- **Python**: Version 3.11 or higher
- **Bing Search API Key**: Get one from [Azure Cognitive Services](https://azure.microsoft.com/services/cognitive-services/bing-web-search-api/)
- **Git**: For cloning the repository

## 🚀 Quick Start

### 1. Clone and Setup

```powershell
# Clone or navigate to the project directory
cd "c:\Users\cyrilbouharb\POCs\S2S Realtime NBK"

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install Azure Developer CLI (azd)
winget install microsoft.azd
```

### 2. Configure Environment

Create a `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Edit the `.env` file and update the following required values:

```ini
# Required: Your Bing Search API key
BING_API_KEY=your-bing-api-key-here

# Optional: Customize these settings
NBK_DOMAIN=nbk.com
```

### 3. Deploy Azure Infrastructure

```powershell
# Login to Azure
az login

# Deploy using Azure Developer CLI
azd up
```

This will:
- Create the resource group: `lab-s2s-realtime-nbk` in `uksouth`
- Deploy API Management (Basicv2 SKU)
- Deploy AI Foundry with AI Services
- Deploy the `gpt-4o-realtime-preview` model automatically
- Configure Application Insights and Log Analytics
- Set up WebSocket API with authentication

### 4. Update .env with Deployment Outputs

After deployment, `azd` will display the outputs. Update your `.env` file:

```ini
APIM_GATEWAY_URL=<from azd output>
APIM_API_KEY=<from azd output>
LOG_ANALYTICS_WORKSPACE_ID=<from azd output>
```

### 5. Run the Application

```powershell
python main.py
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

# Number of search results to use for grounding
MAX_GROUNDING_RESULTS=5

# Freshness of search results (Day, Week, Month)
GROUNDING_FRESHNESS=Month
```

### Realtime API Settings

Customize the voice and behavior:

```ini
# Audio sample rate
SAMPLE_RATE=24000

# Default voice (alloy, ash, ballad, coral, echo, sage, shimmer, verse)
DEFAULT_VOICE=alloy

# Voice activity detection settings
TURN_DETECTION_THRESHOLD=0.4
TURN_DETECTION_SILENCE_MS=600
```

## 💡 Usage Examples

### Interactive Chat Mode

When you run `python main.py`, you'll be prompted to:

1. **Choose deployment option**:
   - Deploy new infrastructure (first time)
   - Use existing resources (subsequent runs)

2. **Ask questions about NBK**:
   ```
   🗣️  You: What are the current interest rates at NBK?
   🗣️  You: Tell me about NBK's digital banking services
   🗣️  You: What are the requirements to open an account at NBK?
   ```

3. **Exit**: Type `quit`, `exit`, or press `Ctrl+C`

### Example Session

```
================================================================================
CONFIGURATION
================================================================================

Azure Settings:
  Resource Group: lab-s2s-realtime-nbk
  Location: uksouth
  Deployment: s2s-realtime-nbk
  APIM SKU: Basicv2

Bing Grounding Settings:
  NBK Domain: nbk.com
  Site Filter: site:nbk.com
  Max Results: 5

Realtime API Settings:
  Sample Rate: 24000 Hz
  Default Voice: alloy
  Modalities: text, audio
================================================================================

╭─────────────────────────────────────────╮
│ Verifying Azure CLI                     │
╰─────────────────────────────────────────╯

✅ Azure CLI verified
ℹ️  User: user@example.com
ℹ️  Subscription: My Subscription
ℹ️  Tenant ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

╭─────────────────────────────────────────╮
│ NBK Realtime Chat with Bing Grounding  │
╰─────────────────────────────────────────╯

ℹ️  Ask questions about NBK (National Bank of Kuwait)
ℹ️  Type 'quit' or 'exit' to end the session

🗣️  You: What services does NBK offer for businesses?

ℹ️  Searching NBK domain for: What services does NBK offer for businesses?
✅ Found 5 relevant results from NBK

╭─────────────────────────────────────────╮
│ Response:                                │
╰─────────────────────────────────────────╯

Based on information from NBK's official website, NBK offers a comprehensive range 
of business banking services including:

1. Business Accounts: Various account types tailored for different business sizes
2. Corporate Loans: Financing solutions for business expansion and operations
3. Trade Finance: Letters of credit, guarantees, and trade services
4. Cash Management: Treasury and cash management solutions
5. Payment Solutions: Corporate cards and digital payment platforms

Source: nbk.com/business-banking
```

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       v
┌─────────────────────────────────┐
│   Python Application            │
│   ┌─────────────────────────┐   │
│   │  Main Application       │   │
│   │  - Chat Interface       │   │
│   │  - Query Processing     │   │
│   └───────┬─────────────────┘   │
│           │                     │
│   ┌───────v──────┐  ┌────────v──────┐
│   │ Bing Search  │  │ Azure OpenAI  │
│   │ (Grounding)  │  │ Realtime API  │
│   └──────────────┘  └───────────────┘
└─────────────────────────────────┘
       │                   │
       v                   v
┌──────────────┐    ┌─────────────────┐
│ Bing Search  │    │  Azure APIM     │
│   API        │    │  ┌───────────┐  │
└──────────────┘    │  │ Realtime  │  │
                    │  │ Endpoint  │  │
                    │  └───────────┘  │
                    └─────────────────┘
                           │
                           v
                    ┌─────────────────┐
                    │  AI Foundry     │
                    │  (GPT Realtime) │
                    └─────────────────┘
```

### Key Components

1. **Main Application (`main.py`)**
   - Orchestrates the entire application flow
   - Manages user interactions
   - Coordinates between Bing grounding and Realtime API

2. **Configuration (`config.py`)**
   - Centralized configuration management
   - Environment variable handling
   - Pydantic-based validation

3. **Utils (`utils.py`)**
   - Azure CLI command execution
   - Bing search integration
   - Deployment management
   - Rich console output

4. **Bicep Templates (`main.bicep` + modules)**
   - Infrastructure as Code
   - Automated Azure resource deployment
   - APIM policy configuration

## 🔐 Security

### API Keys

- Never commit `.env` file to version control
- Store API keys securely
- Use Azure Key Vault for production deployments

### APIM Policies

The application uses APIM for:
- API key management
- Rate limiting
- Request/response logging
- Security policies

### Network Security

- APIM provides a secure gateway
- All traffic encrypted with TLS
- Optional: Configure VNet integration for private endpoints

## 📊 Monitoring

### Application Insights

Monitor your application with:

```powershell
# View logs in Azure Portal
az monitor app-insights component show \
  --resource-group lab-s2s-realtime-nbk \
  --app <app-insights-name>
```

### Log Analytics

Query logs using KQL:

```kql
// Model usage statistics
model_usage

// Prompts and completions
prompts_and_completions

// API Management logs
ApiManagementGatewayLogs
| where TimeGenerated > ago(1h)
```

## 🔧 Troubleshooting

### Common Issues

1. **"Azure CLI not found or not logged in"**
   ```powershell
   az login
   az account show
   ```

2. **"Bing API key not set"**
   - Ensure `BING_API_KEY` is set in `.env`
   - Get a key from [Azure Portal](https://portal.azure.com)

3. **"Deployment failed"**
   - Check Azure permissions
   - Verify resource quotas
   - Review error messages in Azure Portal

4. **"No results found from NBK domain"**
   - Verify Bing API key is valid
   - Check NBK_SITE_FILTER configuration
   - Try a different query

5. **Module import errors**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

### Viewing Deployment Status

```powershell
# Check deployment status
az deployment group show \
  --name s2s-realtime-nbk \
  --resource-group lab-s2s-realtime-nbk

# View deployment operations
az deployment group operation list \
  --name s2s-realtime-nbk \
  --resource-group lab-s2s-realtime-nbk
```

## 🧹 Cleanup

To remove all deployed resources:

```powershell
# Delete the resource group and all resources
az group delete --name lab-s2s-realtime-nbk --yes --no-wait
```

## 📝 Development

### Adding Custom Domains

To ground on multiple domains:

```python
# In config.py, modify BingGroundingConfig
nbk_site_filter: str = Field(
    "(site:nbk.com OR site:nbk.com.kw)",
    alias="NBK_SITE_FILTER"
)
```

### Customizing Voice

Change the default voice in `.env`:

```ini
DEFAULT_VOICE=shimmer  # or alloy, ash, ballad, coral, echo, sage, verse
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
