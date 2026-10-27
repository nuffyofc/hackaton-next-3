// Root orchestration — stubs compose identity + Foundry + ACA modules.
// Re-verify API versions against current Microsoft Learn before first deploy.

@description('Short environment name, e.g. demo or prod')
param environmentName string = 'demo'
param location string = resourceGroup().location

module identity 'modules/identity.bicep' = {
  name: 'identity'
  params: {
    environmentName: environmentName
    location: location
  }
}

module foundry 'modules/foundry-agent.bicep' = {
  name: 'foundry'
  params: {
    environmentName: environmentName
    location: location
  }
}

module aca 'modules/container-apps.bicep' = {
  name: 'aca'
  params: {
    environmentName: environmentName
    location: location
    managedIdentityId: identity.outputs.identityId
  }
}

output identityId string = identity.outputs.identityId
output foundryEndpoint string = foundry.outputs.endpoint
output containerAppName string = aca.outputs.appName
