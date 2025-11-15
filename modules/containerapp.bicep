// Container App for NBK Realtime Backend Proxy

param location string = resourceGroup().location
param suffix string
param containerImage string = 'nginx:latest'  // Placeholder, will be updated by azd
param azureOpenAIEndpoint string
@secure()
param azureOpenAIKey string
param deploymentName string
param apiVersion string

// Container Apps Environment
resource containerAppEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-${suffix}'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'azure-monitor'
    }
  }
}

// Container App for Backend
resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-nbk-backend-${suffix}'
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
      }
      secrets: [
        {
          name: 'azure-openai-key'
          value: azureOpenAIKey
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'nbk-backend'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: azureOpenAIEndpoint
            }
            {
              name: 'AZURE_OPENAI_KEY'
              secretRef: 'azure-openai-key'
            }
            {
              name: 'DEPLOYMENT_NAME'
              value: deploymentName
            }
            {
              name: 'INFERENCE_API_VERSION'
              value: apiVersion
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

output backendUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output backendFqdn string = containerApp.properties.configuration.ingress.fqdn
