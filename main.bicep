// ------------------
//    PARAMETERS
// ------------------

param aiServicesConfig array = []
param modelsConfig array = []
param apimSku string
param apimSubscriptionsConfig array = []
param inferenceAPIPath string = 'inference' // Path to the inference API in the APIM service
param inferenceAPIType string = 'AzureOpenAI'
param foundryProjectName string = 'default'

// ------------------
//    VARIABLES
// ------------------

var resourceSuffix = uniqueString(subscription().id, resourceGroup().id)

// ------------------
//    RESOURCES
// ------------------

// 1. Log Analytics Workspace
module lawModule './modules/workspaces.bicep' = {
  name: 'lawModule'
}

// 2. Application Insights
module appInsightsModule './modules/appinsights.bicep' = {
  name: 'appInsightsModule'
  params: {
    lawId: lawModule.outputs.id
    customMetricsOptedInType: 'WithDimensions'
  }
}

// 3. API Management
module apimModule './modules/apim.bicep' = {
  name: 'apimModule'
  params: {
    apimSku: apimSku
    apimSubscriptionsConfig: apimSubscriptionsConfig
    lawId: lawModule.outputs.id
    appInsightsId: appInsightsModule.outputs.id
    appInsightsInstrumentationKey: appInsightsModule.outputs.instrumentationKey
  }
}

// 4. AI Foundry
module foundryModule './modules/foundry.bicep' = {
    name: 'foundryModule'
    params: {
      aiServicesConfig: aiServicesConfig
      modelsConfig: modelsConfig
      apimPrincipalId: apimModule.outputs.principalId
      foundryProjectName: foundryProjectName
      lawId: lawModule.outputs.id
      appInsightsId: appInsightsModule.outputs.id
      appInsightsInstrumentationKey: appInsightsModule.outputs.instrumentationKey
    }
  }

// 5. Container Registry
module registryModule './modules/registry.bicep' = {
  name: 'registryModule'
  params: {
    suffix: resourceSuffix
  }
}

// 6. Container App Backend (WebSocket Proxy with NBK Knowledge)
module containerAppModule './modules/containerapp.bicep' = {
  name: 'containerAppModule'
  params: {
    suffix: resourceSuffix
    azureOpenAIEndpoint: foundryModule.outputs.extendedAIServicesConfig[0].endpoint
    azureOpenAIKey: foundryModule.outputs.extendedAIServicesConfig[0].key
    deploymentName: 'gpt-realtime'
    apiVersion: '2024-10-01-preview'
    registryServer: registryModule.outputs.loginServer
    registryUsername: registryModule.outputs.name
    registryPassword: registryModule.outputs.adminPassword
  }
}

resource apimService 'Microsoft.ApiManagement/service@2024-06-01-preview' existing = {
  name: 'apim-${resourceSuffix}'
  dependsOn: [
    foundryModule
  ]
}

// 7. APIM OpenAI-RT Websocket API (routes to Container App Backend)
// https://learn.microsoft.com/azure/templates/microsoft.apimanagement/service/apis
resource api 'Microsoft.ApiManagement/service/apis@2024-06-01-preview' = {
  name: 'realtime-audio'
  parent: apimService
  properties: {
    apiType: 'websocket'
    description: 'Inference API for NBK Realtime (via backend proxy)'
    displayName: 'InferenceAPI'
    path: '${inferenceAPIPath}/openai/realtime'
    serviceUrl: 'wss://${containerAppModule.outputs.backendFqdn}/realtime'
    type: inferenceAPIType
    protocols: [
      'wss'
    ]
    subscriptionKeyParameterNames: {
      header: 'api-key'
      query: 'api-key'
    }
    subscriptionRequired: true
  }
}

resource rtOperation 'Microsoft.ApiManagement/service/apis/operations@2024-06-01-preview' existing = {
  name: 'onHandshake'
  parent: api
}

// https://learn.microsoft.com/azure/templates/microsoft.apimanagement/service/apis/policies
resource rtPolicy 'Microsoft.ApiManagement/service/apis/operations/policies@2024-06-01-preview' = {
  name: 'policy'
  parent: rtOperation
  properties: {
    format: 'rawxml'
    value: loadTextContent('policy.xml')
  }
}

resource apiDiagnostics 'Microsoft.ApiManagement/service/apis/diagnostics@2024-06-01-preview' = {
  parent: api
  name: 'azuremonitor'
  properties: {
    alwaysLog: 'allErrors'
    verbosity: 'verbose'
    logClientIp: true
    loggerId: apimModule.outputs.loggerId
    sampling: {
      samplingType: 'fixed'
      percentage: json('100')
    }
    frontend: {
      request: {
        headers: []
        body: {
          bytes: 0
        }
      }
      response: {
        headers: []
        body: {
          bytes: 0
        }
      }
    }
    backend: {
      request: {
        headers: []
        body: {
          bytes: 0
        }
      }
      response: {
        headers: []
        body: {
          bytes: 0
        }
      }
    }
    largeLanguageModel: {
      logs: 'enabled'
      requests: {
        messages: 'all'
        maxSizeInBytes: 262144
      }
      responses: {
        messages: 'all'
        maxSizeInBytes: 262144
      }
    }
  }
} 


resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: 'workspace-${resourceSuffix}'
  dependsOn: [
    foundryModule
  ]
}

resource modelUsageFunction 'Microsoft.OperationalInsights/workspaces/savedSearches@2025-02-01' = {
  parent: logAnalytics
  name: '${guid(subscription().subscriptionId, resourceGroup().id)}_model_usage'
  properties: {
    category: 'llm'
    displayName: 'model_usage'
    version: 2
    functionAlias: 'model_usage'
    query: 'let llmHeaderLogs = ApiManagementGatewayLlmLog \r\n| where DeploymentName != \'\'; \r\nlet llmLogsWithSubscriptionId = llmHeaderLogs \r\n| join kind=leftouter ApiManagementGatewayLogs on CorrelationId \r\n| project \r\n    SubscriptionId = ApimSubscriptionId, DeploymentName, PromptTokens, CompletionTokens, TotalTokens; \r\nllmLogsWithSubscriptionId \r\n| summarize \r\n    SumPromptTokens      = sum(PromptTokens), \r\n    SumCompletionTokens      = sum(CompletionTokens), \r\n    SumTotalTokens      = sum(TotalTokens) \r\n  by SubscriptionId, DeploymentName'
  }
}

resource promptsAndCompletionsFunction 'Microsoft.OperationalInsights/workspaces/savedSearches@2025-02-01' = {
  parent: logAnalytics
  name: '${guid(subscription().subscriptionId, resourceGroup().id)}_prompts_and_completions'
  properties: {
    category: 'llm'
    displayName: 'prompts_and_completions'
    version: 2
    functionAlias: 'prompts_and_completions'
    query: 'ApiManagementGatewayLlmLog\r\n| extend RequestArray = parse_json(RequestMessages)\r\n| extend ResponseArray = parse_json(ResponseMessages)\r\n| mv-expand RequestArray\r\n| mv-expand ResponseArray\r\n| project\r\n    CorrelationId, \r\n    RequestContent = tostring(RequestArray.content), \r\n    ResponseContent = tostring(ResponseArray.content)\r\n| summarize \r\n    Input = strcat_array(make_list(RequestContent), " . "), \r\n    Output = strcat_array(make_list(ResponseContent), " . ")\r\n    by CorrelationId\r\n| where isnotempty(Input) and isnotempty(Output)\r\n'
  }
}

// MCP server modules removed - not needed for Bing grounding scenario

// ------------------
//    OUTPUTS
// ------------------

output logAnalyticsWorkspaceId string = lawModule.outputs.customerId
output apimServiceId string = apimModule.outputs.id
output apimResourceGatewayURL string = apimModule.outputs.gatewayUrl
output apimSubscriptions array = apimModule.outputs.apimSubscriptions

// Frontend Connection Information
output APIM_GATEWAY_URL string = apimModule.outputs.gatewayUrl
output APIM_SUBSCRIPTION_KEY string = apimModule.outputs.apimSubscriptions[0].key
output APIM_SUBSCRIPTION_NAME string = apimModule.outputs.apimSubscriptions[0].displayName
output WEBSOCKET_ENDPOINT string = 'wss://${replace(apimModule.outputs.gatewayUrl, 'https://', '')}/${inferenceAPIPath}/openai/realtime'
output API_VERSION string = '2024-10-01-preview'
output FULL_WEBSOCKET_URL string = 'wss://${replace(apimModule.outputs.gatewayUrl, 'https://', '')}/${inferenceAPIPath}/openai/realtime?api-version=2024-10-01-preview&deployment=gpt-realtime'
output RESOURCE_GROUP_NAME string = resourceGroup().name
output DEPLOYMENT_REGION string = resourceGroup().location
output BACKEND_URL string = containerAppModule.outputs.backendUrl
output BACKEND_FQDN string = containerAppModule.outputs.backendFqdn
output SERVICE_BACKEND_NAME string = containerAppModule.outputs.containerAppName
output AZURE_CONTAINER_APP_NAME string = containerAppModule.outputs.containerAppName
output AZURE_CONTAINER_APPS_ENVIRONMENT_NAME string = 'cae-${resourceSuffix}'
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = registryModule.outputs.endpoint
output AZURE_CONTAINER_REGISTRY_NAME string = registryModule.outputs.name
