#!/bin/bash
# NBK Voice Assistant - Simple Deployment Script
# Uses only Azure CLI (az) commands - no Docker or azd needed!

set -e  # Exit on error

# Configuration
RESOURCE_GROUP="rg-nbk-voice"
LOCATION="swedencentral"
ENV_NAME="nbk-prod"

echo "🚀 NBK Voice Assistant Deployment"
echo "=================================="
echo ""
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo ""

# Step 1: Create Resource Group
echo "📦 Step 1/4: Creating resource group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION \
  --output none

echo "✅ Resource group created"
echo ""

# Step 2: Deploy Infrastructure
echo "🏗️  Step 2/4: Deploying infrastructure (Azure OpenAI, APIM, Container Registry, Container App)..."
echo "This may take 5-10 minutes..."
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file main.bicep \
  --parameters @main.parameters.json \
  --parameters environmentName=$ENV_NAME \
  --name main \
  --output none

echo "✅ Infrastructure deployed"
echo ""

# Step 3: Build Docker Image in ACR (Cloud Build - no local Docker needed!)
echo "🐳 Step 3/4: Building backend container image in Azure..."
ACR_NAME=$(az deployment group show \
  -g $RESOURCE_GROUP \
  -n main \
  --query properties.outputs.AZURE_CONTAINER_REGISTRY_NAME.value \
  -o tsv)

echo "Building image in ACR: $ACR_NAME"
az acr build \
  --registry $ACR_NAME \
  --image nbk-backend:latest \
  --platform linux/amd64 \
  --file Dockerfile \
  . \
  --output none

echo "✅ Container image built and pushed to ACR"
echo ""

# Step 4: Update Container App with Image
echo "🚀 Step 4/4: Deploying backend to Container App..."
CONTAINER_APP_NAME=$(az deployment group show \
  -g $RESOURCE_GROUP \
  -n main \
  --query properties.outputs.AZURE_CONTAINER_APP_NAME.value \
  -o tsv)

az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image ${ACR_NAME}.azurecr.io/nbk-backend:latest \
  --output none

echo "✅ Backend deployed"
echo ""

# Get Outputs
echo "🎉 Deployment Complete!"
echo "======================="
echo ""
echo "📋 Your WebSocket Connection Details:"
echo ""

APIM_URL=$(az deployment group show -g $RESOURCE_GROUP -n main --query properties.outputs.APIM_GATEWAY_URL.value -o tsv)
APIM_KEY=$(az deployment group show -g $RESOURCE_GROUP -n main --query properties.outputs.APIM_SUBSCRIPTION_KEY.value -o tsv)
FULL_WS_URL=$(az deployment group show -g $RESOURCE_GROUP -n main --query properties.outputs.FULL_WEBSOCKET_URL.value -o tsv)

echo "APIM Gateway: $APIM_URL"
echo "API Key: $APIM_KEY"
echo ""
echo "Complete WebSocket URL:"
echo "${FULL_WS_URL}&api-key=${APIM_KEY}"
echo ""
echo "🔍 View resources in Azure Portal:"
echo "https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/overview"
echo ""
echo "✅ Ready to use!"
