# NBK Voice Assistant - Quick Deployment Guide

## ✅ Recommended: Use azd (One Command)

**This is the easiest and most reliable way to deploy everything!**

```powershell
# Option 1: Use the deploy script (recommended)
./deploy.ps1

# Option 2: Run azd directly
azd up
```

### What `azd up` does automatically:
1. ✅ Creates all Azure resources (AI Foundry, APIM, ACR, Container App)
2. ✅ Builds Docker image **in Azure** (no local Docker needed!)
3. ✅ Pushes image to Azure Container Registry
4. ✅ Deploys container to Container App
5. ✅ Runs post-provision hook (scrapes NBK knowledge)
6. ✅ Outputs WebSocket URL and API key

**Time:** 10-15 minutes  
**Requirements:** Azure Developer CLI (`azd`) only

---

## 📋 Prerequisites

1. **Install Azure Developer CLI:**
   ```powershell
   winget install Microsoft.Azd
   ```
   Or visit: https://aka.ms/install-azd

2. **Login to Azure:**
   ```powershell
   azd auth login
   ```

3. **Python 3.11+** (for post-provision hook)

---

## 🚀 Deployment Steps

### First Time Deployment

```powershell
# 1. Run the deployment script
./deploy.ps1

# 2. When prompted:
#    - Enter environment name (e.g., "nbk-prod")
#    - Confirm deployment (Y)

# 3. Wait for completion (~10-15 minutes)

# 4. Copy the WebSocket URL and API key from the output
```

### Update Existing Deployment

```powershell
# Deploy code changes only (fast!)
azd deploy

# Update everything (infra + code)
azd up
```

---

## 🔧 Key Features

### Remote Docker Build
- The `azure.yaml` is configured with `remoteBuild: true`
- Docker images are built in Azure Container Registry
- **No local Docker installation needed!**
- Faster builds using Azure's infrastructure

### Automatic Configuration
- Post-provision hook automatically scrapes NBK website
- Creates `nbk_knowledge.json` with latest content
- Configures environment variables
- Outputs ready-to-use WebSocket endpoint

### Resource Management
```powershell
# View environment variables
azd env get-values

# View logs
azd monitor

# View resources in Azure Portal
azd show

# Delete everything
azd down
```

---

## 📁 Project Structure

```
.
├── azure.yaml              # azd configuration (with remoteBuild)
├── main.bicep              # Infrastructure as Code
├── main.parameters.json    # Deployment parameters
├── Dockerfile              # Container definition
├── deploy.ps1              # Deployment wrapper script
├── backend/
│   ├── main.py            # FastAPI WebSocket proxy
│   └── requirements.txt   # Python dependencies
├── infra/
│   └── hooks/
│       └── postprovision.ps1  # Post-deployment automation
└── modules/               # Bicep modules for each resource
```

---

## 🐛 Troubleshooting

### "azd not found"
```powershell
# Install azd
winget install Microsoft.Azd

# Verify installation
azd version
```

### "Not authenticated"
```powershell
azd auth login
```

### "Deployment failed"
```powershell
# Check detailed logs
azd show

# View specific resource logs
azd monitor

# Clean up and retry
azd down
azd up
```

### "Docker build failed"
- This shouldn't happen with `remoteBuild: true`
- The build happens in Azure, not locally
- Check ACR logs in Azure Portal if issues occur

---

## ⚡ Quick Commands

```powershell
# Deploy everything from scratch
azd up

# Deploy code changes only
azd deploy

# View deployment info
azd show

# Get environment variables
azd env get-values

# View logs in real-time
azd monitor

# Delete everything
azd down

# Run the deployment script
./deploy.ps1
```

---

## 🎯 What You Get

After successful deployment:

- **WebSocket Endpoint:** `wss://apim-xxx.azure-api.net/realtime-audio/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime`
- **API Key:** Your subscription key for authentication
- **Resource Group:** All resources in one group for easy management
- **Container App:** Auto-scaling backend with NBK knowledge
- **APIM Gateway:** Managed WebSocket endpoint with monitoring

---

## 💡 Why azd?

| Feature | azd | Manual az CLI |
|---------|-----|---------------|
| Setup Time | 1 command | 10+ commands |
| Docker Build | Built-in | Manual setup |
| Environment Management | Automatic | Manual .env files |
| Idempotency | Built-in | Manual checks |
| Cleanup | `azd down` | Find/delete each resource |
| Updates | `azd deploy` | Rebuild + redeploy manually |

**Bottom line:** Use `azd up` or `./deploy.ps1` - it's designed for this! 🚀
