/**
 * @module deployments
 * @description This module defines model deployments for Azure OpenAI
 */

// ------------------
//    PARAMETERS
// ------------------

@description('The name of the Azure Cognitive Services account')
param cognitiveServiceName string

@description('Configuration array for the model deployments')
param modelsConfig array = []

// ------------------
//    RESOURCES
// ------------------

resource cognitiveService 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  name: cognitiveServiceName
}

resource deployments 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = [for model in modelsConfig: {
  parent: cognitiveService
  name: model.name
  sku: {
    name: model.sku
    capacity: model.capacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: model.name
      version: model.version
    }
    versionUpgradeOption: 'OnceCurrentVersionExpired'
  }
}]

// ------------------
//    OUTPUTS
// ------------------

output deploymentNames array = [for (model, i) in modelsConfig: deployments[i].name]
