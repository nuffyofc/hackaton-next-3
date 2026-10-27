// Minimal Foundry / AI Services account placeholder.
// Confirm kind, SKU, and model deployment against current docs before deploy.

param environmentName string
param location string = resourceGroup().location
param modelDeploymentName string = 'gpt-4o-mini'

var accountName = 'aif-${environmentName}-${uniqueString(resourceGroup().id)}'

resource foundryAccount 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: accountName
  location: location
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    disableLocalAuth: true
    customSubDomainName: accountName
  }
}

output endpoint string = foundryAccount.properties.endpoint
output accountName string = foundryAccount.name
output modelDeploymentName string = modelDeploymentName
