#!/bin/bash
# Update Backend Only - Quick backend code updates

set -e

RESOURCE_GROUP="rg-nbk-voice"

echo "🔄 Updating NBK Backend..."
echo ""

# Get deployment outputs
ACR_NAME=$(az deployment group show -g $RESOURCE_GROUP -n main --query properties.outputs.AZURE_CONTAINER_REGISTRY_NAME.value -o tsv)
CONTAINER_APP_NAME=$(az deployment group show -g $RESOURCE_GROUP -n main --query properties.outputs.AZURE_CONTAINER_APP_NAME.value -o tsv)

echo "📦 Building new image in ACR..."
az acr build \
  --registry $ACR_NAME \
  --image nbk-backend:latest \
  --platform linux/amd64 \
  --file Dockerfile \
  . \
  --output none

echo "🚀 Updating Container App..."
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image ${ACR_NAME}.azurecr.io/nbk-backend:latest \
  --output none

echo ""
echo "✅ Backend updated successfully!"
echo ""
echo "Check logs:"
echo "az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --follow"
