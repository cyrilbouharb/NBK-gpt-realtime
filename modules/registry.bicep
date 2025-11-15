// Azure Container Registry for backend Docker images

param location string = resourceGroup().location
param suffix string

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: 'acrnbk${suffix}'
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

output name string = registry.name
output loginServer string = registry.properties.loginServer
output endpoint string = registry.properties.loginServer
@secure()
output adminPassword string = registry.listCredentials().passwords[0].value
